#!/usr/bin/env python
"""
Script to search aur-requests mailing list archives for information about
a package.

List: https://lists.archlinux.org/listinfo/aur-requests

Requirements
============

requests

"""

import sys
import os
import argparse
import logging
import requests
from time import time
from mailbox import mbox
from base64 import b64decode

FORMAT = "[%(asctime)s %(levelname)s] %(message)s"
logging.basicConfig(level=logging.WARNING, format=FORMAT)
logger = logging.getLogger()


class AurRequestSearcher(object):

    archive_url = 'https://lists.archlinux.org/pipermail/' \
                  'aur-requests.mbox/aur-requests.mbox'

    def __init__(self):
        """ init method, run at class creation """
        self._apath = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), 'aur-requests.mbox'
        )

    def run(self, search):
        search = search.lower()
        self._get_archive()
        logger.info('Loading mbox from %s', self._apath)
        box = mbox(self._apath)
        logger.info('Searching messages...')
        for key, msg in box.items():
            try:
                if search not in msg['Subject'].lower():
                    continue
                print('%s: %s' % (msg['Date'], msg['Subject']))
                payload = msg.get_payload()
                if isinstance(payload, type([])):
                    for p in payload:
                        print(p)
                else:
                    enc = msg['Content-Transfer-Encoding']
                    if enc == 'base64':
                        print(b64decode(payload).decode('utf-8'))
                    else:
                        print(payload)
                print('############################################')
            except Exception:
                logger.error('Unable to load message: %s', key, exc_info=True)

    def _get_archive(self):
        if os.path.exists(self._apath):
            mtime = os.path.getmtime(self._apath)
            if mtime >= (time() - 86400):
                logger.debug('Archive is less than 1 day old; using existing')
                return
        logger.warning('Downloading list archive; this may take some time')
        r = requests.get(self.archive_url, stream=True)
        with open(self._apath, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        logger.info('Finished downloading archive to: %s', self._apath)

def parse_args(argv):
    """
    parse arguments/options

    this uses the new argparse module instead of optparse
    see: <https://docs.python.org/2/library/argparse.html>
    """
    p = argparse.ArgumentParser(description='Search AUR Requests archive')
    p.add_argument('-v', '--verbose', dest='verbose', action='count', default=0,
                   help='verbose output. specify twice for debug-level output.')
    p.add_argument('SEARCH', action='store', type=str,
                   help='string to search message subjects for')
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

    AurRequestSearcher().run(args.SEARCH)
