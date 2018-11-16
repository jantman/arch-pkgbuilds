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

FORMAT = "[%(asctime)s %(levelname)s] %(message)s"
logging.basicConfig(level=logging.WARNING, format=FORMAT)
logger = logging.getLogger()


class ArchRebuilder(object):

    def run(self):
        """ do stuff here """
        pkgnames = self._list_packages()
        logger.info(
            'Found %d packages in directory: %s', len(pkgnames), pkgnames
        )
        to_upgrade = []
        for name in pkgnames:
            curr = self.current_package_version(name)
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

    def current_package_version(self, pkg_name):
        """Return current version of package in pwd"""
        logger.debug('Getting current package version for: %s', pkg_name)
        fpath = os.path.realpath(os.path.join(pkg_name, 'PKGBUILD'))
        cmd = ['/bin/bash', '-c', 'source %s && echo $pkgver' % fpath]
        logger.debug('Run: %s', ' '.join(cmd))
        p = subprocess.run(cmd, capture_output=True)
        assert p.returncode == 0
        ver = p.stdout.decode().strip()
        cmd = ['/bin/bash', '-c', 'source %s && echo $pkgrel' % fpath]
        logger.debug('Run: %s', ' '.join(cmd))
        p = subprocess.run(cmd, capture_output=True)
        assert p.returncode == 0
        rel = p.stdout.decode().strip()
        return '%s-%s' % (ver, rel)

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

    ArchRebuilder().run()
