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

FORMAT = "[%(asctime)s %(levelname)s] %(message)s"
logging.basicConfig(level=logging.WARNING, format=FORMAT)
logger = logging.getLogger()


class ArchRebuilder(object):

    def __init__(self, repofile):
        self._repofile = repofile

    def run(self):
        """ do stuff here """
        pkgnames = self._list_packages()
        logger.info(
            'Found %d packages in directory: %s', len(pkgnames), pkgnames
        )
        pkginfo = self.read_repo_file()
        latest_versions = self.latest_package_versions(pkgnames)
        to_upgrade = []
        for name in pkgnames:
            curr = pkginfo.get(name, {'VERSION': 'NONE'})['VERSION']
            latest = latest_versions[name]
            logger.info('Package %s current=%s latest=%s', name, curr, latest)
            if curr != latest:
                to_upgrade.append(name)
        logger.info(
            'Found %d packages to update: %s', len(to_upgrade), to_upgrade
        )
        for pkgname in to_upgrade:
            self._update_pkg(pkgname)
            self._build_pkg(pkgname)
        self.prune_repo()

    def _update_pkg(self, pkg_name):
        raise NotImplementedError()

    def _build_pkg(self, pkg_name):
        raise NotImplementedError()
        # self._copy_to_repo(fname)

    def _copy_to_repo(self, fname):
        raise NotImplementedError()

    def prune_repo(self):
        raise NotImplementedError()

    def _list_packages(self):
        """Return a list of string package names in pwd"""
        res = []
        logger.debug('Listing packages in repo directory')
        for fname in glob(
            os.path.join(
                os.path.realpath(os.path.dirname(__file__)), '*', 'PKGBUILD'
            )
        ):
            res.append(fname.split('/')[-2])
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
            raise RuntimeError(
                'ERROR: Requested info for %d packages but got %d results' % (
                    len(pkg_names), len(j['results'])
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
    elif args.verbose == 1:
        set_log_info()

    ArchRebuilder(args.REPO_TAR_GZ).run()
