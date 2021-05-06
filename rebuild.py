#!/usr/bin/env python3
"""
Arch Linux pkgbuild rebuild script.

Rather naive right now.
"""

import sys
import argparse
import logging
from glob import glob
import re
import os
import requests
import subprocess
import tarfile
import shutil

FORMAT = "[%(asctime)s %(levelname)s] %(message)s"
logging.basicConfig(level=logging.WARNING, format=FORMAT)
logger = logging.getLogger()

IGNORE_PACKAGES = ['lego-git', 'linux-precision5530', 'aws-session-manager-plugin-jantman', 'brother-mfc-j5945dw']


class ArchRebuilder(object):

    def __init__(self, repofile):
        self._repofile = os.path.realpath(os.path.abspath(repofile))
        self._topdir = os.path.realpath(os.path.dirname(__file__))

    def run(self, skip_packages=[], only_packages=[]):
        """ do stuff here """
        pkgnames = self._list_packages()
        logger.info(
            'Found %d packages in directory: %s', len(pkgnames), pkgnames
        )
        pkginfo = self.read_repo_file()
        repo_files = {
            x['FILENAME']: x['NAME'] for x in pkginfo.values()
        }
        logger.debug('Repo current files: %s', repo_files)
        repodir = os.path.dirname(self._repofile)
        for fname, pkname in repo_files.items():
            fpath = os.path.join(repodir, fname)
            if not os.path.exists(fpath):
                raise RuntimeError(
                    f'ERROR: File for {pkname} ({fname}) is in repo but '
                    'does not exist on disk!'
                )
        latest_versions = self.latest_package_versions(pkgnames)
        to_upgrade = []
        for name in pkgnames:
            curr = pkginfo.get(name, {'VERSION': 'NONE'})['VERSION']
            latest = latest_versions[name]
            logger.info('Package %s current=%s latest=%s', name, curr, latest)
            if name in skip_packages:
                print('Skipping: %s' % name)
                continue
            if len(only_packages) > 0 and name not in only_packages:
                print('Skipping: %s' % name)
                continue
            if curr != latest:
                to_upgrade.append(name)
        logger.info(
            'Found %d packages to update: %s', len(to_upgrade), to_upgrade
        )
        keep_versions = []
        for pkgname in to_upgrade:
            keep_versions.append((pkgname, latest_versions[pkgname]))
            rev = self._update_pkg(pkgname)
            pk_path = self._build_pkg(pkgname, rev)
            self._run_cmd(
                [
                    'repo-add', '-R', '-n',
                    'jantman.db.tar.gz',
                    os.path.basename(pk_path)
                ],
                cwd=repodir
            )
        logger.info('Successfully built all %d packages', len(to_upgrade))
        self.prune_repo(latest_versions, repo_files)

    def _update_pkg(self, pkg_name):
        logger.info('Updating package: %s', pkg_name)
        dest_dir = os.path.join(self._topdir, pkg_name)
        if os.path.exists(dest_dir):
            logger.debug('Removing existing directory: %s', dest_dir)
            shutil.rmtree(dest_dir)
        assert self._run_cmd([
            'git', 'clone', '--depth=1',
            'https://aur.archlinux.org/%s.git' % pkg_name, dest_dir
        ]).returncode == 0
        rev = self._run_cmd(
            ['git', 'rev-parse', 'HEAD'], cwd=dest_dir
        ).stdout.decode().strip()
        pkver = self._run_cmd(
            [
                '/bin/bash',
                '-c',
                'source PKGBUILD && echo "${pkgver}-${pkgrel}"'
            ],
            cwd=dest_dir
        ).stdout.decode().strip()
        assert self._run_cmd(['git', 'add', dest_dir]).returncode == 0
        logger.info('%s updated to %s (AUR commit %s)', pkg_name, pkver, rev)
        return rev

    def _run_cmd(self, cmd, cwd=None):
        if cwd is None:
            logger.debug('Executing: %s', ' '.join(cmd))
        else:
            logger.debug('Executing in %s: %s', cwd, ' '.join(cmd))
        p = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=cwd
        )
        logger.debug('Command exited %d: %s', p.returncode, p.stdout.decode())
        if p.returncode != 0:
            logger.warning(
                'Command %s exited %d:\n%s', ' '.join(cmd),
                p.returncode, p.stdout.decode()
            )
        return p

    def _build_pkg(self, pkg_name, rev):
        logger.info('Building: %s', pkg_name)
        os.chdir(os.path.join(self._topdir, pkg_name))
        before_files = glob('**/*', recursive=True)
        p = self._run_cmd(['makepkg'])
        if p.returncode != 0:
            raise RuntimeError(
                'makepkg for %s failed:\n%s' % (pkg_name, p.stdout.decode())
            )
        new_files = list(
            set(glob('**/*', recursive=True)) - set(before_files)
        )
        logger.debug('makepkg generated new files: %s', new_files)
        # for packages build from git, get the version after building
        pkg_ver = self._run_cmd(
            [
                '/bin/bash',
                '-c',
                'source PKGBUILD && echo "${pkgver}-${pkgrel}"'
            ]
        ).stdout.decode().strip()
        packages = [
            x for x in new_files if (
                x.startswith('%s-%s-' % (pkg_name, pkg_ver)) or
                x.startswith('%s-1:%s-' % (pkg_name, pkg_ver))
            )
            and (
                x.endswith('.pkg.tar.xz') or x.endswith('.pkg.tar.zst')
            )
        ]
        if len(packages) != 1:
            raise RuntimeError(
                'ERROR: Unable to find built package from %d candidates: %s' % (
                    len(packages), packages
                )
            )
        logger.info('Built package: %s', os.path.realpath(packages[0]))
        newpath = os.path.join(
            os.path.dirname(os.path.realpath(self._repofile)),
            os.path.basename(packages[0])
        )
        logger.info('Moving package to: %s', newpath)
        os.rename(os.path.realpath(packages[0]), newpath)
        assert self._run_cmd(['git', 'add', '.']).returncode == 0
        r = self._run_cmd([
            'git', 'commit', '-m',
            'rebuild.py - pull in %s-%s from AUR at commit %s' % (
                pkg_name, pkg_ver, rev
            )
        ])
        if (
            r.returncode != 0 and
            'nothing to commit, working tree clean' not in r.stdout.decode()
        ):
            raise RuntimeError('ERROR: git commit failed %d:\n%s' % (
                r.returncode, r.stdout.decode()
            ))
        os.chdir(self._topdir)
        return newpath

    def prune_repo(self, name_ver_to_keep, repo_files):
        logger.info('Pruning old packages from repo...')
        logger.debug('Keep: %s', name_ver_to_keep)
        repodir = os.path.dirname(self._repofile)
        repofiles = [os.path.basename(x) for x in glob(
            os.path.join(repodir, '*.pkg.tar.xz')
        )]
        repofiles.extend([os.path.basename(x) for x in glob(
            os.path.join(repodir, '*.pkg.tar.zst')
        )])
        logger.info('Found %d packages currently in repo', len(repofiles))
        logger.debug('Files in repo: %s', repofiles)
        for pkname, pkver in name_ver_to_keep.items():
            for arch in ['x86_64', 'any']:
                fname = '%s-%s-%s.pkg.tar.xz' % (pkname, pkver, arch)
                if fname in repofiles:
                    repofiles.remove(fname)
                fname = '%s-%s-%s.pkg.tar.zst' % (pkname, pkver, arch)
                if fname in repofiles:
                    repofiles.remove(fname)
        for pkname in IGNORE_PACKAGES:
            for fname in repofiles:
                if fname.startswith(pkname):
                    repofiles.remove(fname)
        logger.info(
            'Found %d orphaned packages to remove: %s',
            len(repofiles), ' '.join(repofiles)
        )
        for fname in repofiles:
            if fname not in repo_files:
                raise RuntimeError(f'ERROR: {fname} not found in repo!')
            p = os.path.join(repodir, fname)
            self._run_cmd(
                [
                    'repo-remove',
                    'jantman.db.tar.gz',
                    fname
                ],
                cwd=repodir
            )
            logger.warning('Unlink: %s', p)
            os.unlink(p)

    def _list_packages(self):
        """Return a list of string package names in pwd"""
        res = []
        logger.debug('Listing packages in repo directory')
        for fname in glob(os.path.join(self._topdir, '*', 'PKGBUILD')):
            tmp = fname.split('/')[-2]
            if tmp not in IGNORE_PACKAGES:
                res.append(tmp)
        return sorted(res)

    def read_repo_file(self):
        """
        Read a repository .tar.gz; return dict of package name to dict info
        """
        logger.debug('Opening %s as gzipped tarfile', self._repofile)
        res = {}
        with tarfile.open(self._repofile, 'r:gz') as tar:
            for f in tar.getmembers():
                if f.name.endswith('/desc'):
                    tmp = self._repo_file_info(tar.extractfile(f))
                    res[tmp['NAME']] = tmp
        return res

    def _repo_file_info(self, f):
        """
        :param f: File in an Arch repo .tar.gz
        :type f: io.BufferedReader
        :return: dict of key/value pairs for the package info
        :rtype: dict
        """
        key = None
        items = []
        result = {}
        for line in f.readlines():
            line = line.decode().strip()
            if key is None and line.startswith('%') and line.endswith('%'):
                key = line.strip('%')
                continue
            if line == '':
                if len(items) == 1:
                    result[key] = items[0]
                else:
                    result[key] = items
                key = None
                items = []
                continue
            items.append(line)
        return result

    def latest_package_versions(self, pkg_names):
        """Return latest version of package on AUR"""
        logger.info('Getting latest package versions')
        url = 'https://aur.archlinux.org/rpc/?v=5&type=info&arg[]=%s' % \
            '&arg[]='.join(pkg_names)
        logger.debug('GET %s', url)
        r = requests.get(url)
        r.raise_for_status()
        j = r.json()
        if j.get('type', '') == 'error':
            raise RuntimeError(
                'ERROR getting info for package %s: %s', pkg_name, r.content
            )
        if len(j['results']) != len(pkg_names):
            diff = set(pkg_names).difference(
                set([x['Name'] for x in j['results']])
            )
            raise RuntimeError(
                'ERROR: Requested info for %d packages but got %d results; '
                'missing from query results: %s' % (
                    len(pkg_names), len(j['results']), diff
                )
            )
        logger.debug('AUR response: %s', r.content)
        return {
            x['Name']: x['Version'] for x in j['results']
        }


def parse_args(argv):
    """
    parse arguments/options

    this uses the new argparse module instead of optparse
    see: <https://docs.python.org/2/library/argparse.html>
    """
    p = argparse.ArgumentParser(description='Arch rebuild script')
    p.add_argument('-v', '--verbose', dest='verbose', action='count', default=0,
                   help='verbose output. specify twice for debug-level output.')
    p.add_argument('-s', '--skip', dest='skip', action='append', default=[],
                   help='Skip building these package(s)')
    p.add_argument('-o', '--only', dest='only', action='append', default=[],
                   help='Only build these packages')
    p.add_argument('REPO_TAR_GZ', action='store', type=str,
                   help='Path to repo .tar.gz file')
    args = p.parse_args(argv)
    return args

def set_log_info():
    """set logger level to INFO"""
    set_log_level_format(logging.INFO,
                         '%(asctime)s %(levelname)s:%(name)s:%(message)s')


def set_log_debug():
    """set logger level to DEBUG, and debug-level output format"""
    set_log_level_format(
        logging.DEBUG,
        "%(asctime)s [%(levelname)s %(filename)s:%(lineno)s - "
        "%(name)s.%(funcName)s() ] %(message)s"
    )


def set_log_level_format(level, format):
    """
    Set logger level and format.

    :param level: logging level; see the :py:mod:`logging` constants.
    :type level: int
    :param format: logging formatter format string
    :type format: str
    """
    formatter = logging.Formatter(fmt=format)
    logger.handlers[0].setFormatter(formatter)
    logger.setLevel(level)

if __name__ == "__main__":
    args = parse_args(sys.argv[1:])

    # set logging level
    if args.verbose > 1:
        set_log_debug()
    else:
        set_log_info()

    ArchRebuilder(args.REPO_TAR_GZ).run(args.skip, args.only)
