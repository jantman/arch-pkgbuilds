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
        to_upgrade = []
        for name in pkgnames:
            curr = pkginfo[name]['VERSION']
            latest = self.latest_package_version(name)
            logger.info('Package %s: current=%s latest=%s', name, curr, latest)
            if curr != latest:
                to_upgrade.append(name)
        logger.info(
            'Found %d packages to update: %s', len(to_upgrade), to_upgrade
        )

    def _list_packages(self):
        """Return a list of string package names in pwd"""
        res = []
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

    def latest_package_version(self, pkg_name):
        """Return latest version of package on AUR"""
        logger.debug('Getting latest package version for: %s', pkg_name)
        r = requests.get(
            'https://aur.archlinux.org/rpc/?v=5&type=info&arg[]=%s' % pkg_name
        )
        r.raise_for_status()
        j = r.json()
        if j.get('type', '') == 'error':
            raise RuntimeError(
                'ERROR getting info for package %s: %s', pkg_name, r.content
            )
        if len(j['results']) != 1:
            raise RuntimeError(
                'ERROR: Requested info for package %s but got %d results' % (
                    pkg_name, len(j['results'])
                )
            )
        logger.debug('AUR response: %s', r.content)
        return j['results'][0]['Version']


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
