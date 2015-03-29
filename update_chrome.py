#!/usr/bin/env python

import requests
import os
import logging
import email

FORMAT = "[%(levelname)s %(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
logging.basicConfig(level=logging.ERROR, format=FORMAT)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

repo_base_url = 'https://dl.google.com/linux/chrome/deb'
logger.debug("repo_base_url={b}".format(b=repo_base_url))
pkgbuild_name = 'google-chrome.PKGBUILD'

def parse_deb_repo_packages(packages_url):
    """
    Parse a Debian repository Packages file (https://wiki.debian.org/RepositoryFormat),
    return a list of Package information contained in the file.
    """
    r = requests.get(packages_url)
    if r.status_code != 200:
        logger.error("Error: got status code {s} for url {u}".format(s=r.status_code, u=packages_url))
        raise SystemExit(1)
    packages = []
    entries = r.text.split('\n\n')
    for entry in entries:
        t = email.message_from_string(entry)
        titems = t.items()
        entry_dict = {hfield: hval for hfield, hval in titems}
        if len(entry_dict) == 0:
            continue
        packages.append(entry_dict)
    return packages

def get_package_info(packages_path):
    """get the package information for the PKGBUILD, for the specified architecture"""
    packages_url = repo_base_url + packages_path
    logger.info("Using repository packages file: {p}".format(p=packages_url))
    packages = parse_deb_repo_packages(packages_url)

    # find the current stable package
    for package in packages:
        if package['Package'] == 'google-chrome-stable':
            break

    logger.info("Found package: {p} ({a}) {v}".format(
        p=package['Package'],
        a=package['Architecture'],
        v=package['Version'])
    )

    if '-' in package['Version']:
        version, release = package['Version'].split('-')
    else:
        version = package['Version']
        release = 0

    pkg_path = repo_base_url + '/' + package['Filename']
    logger.info("Package path: {p}".format(p=pkg_path))
    result = {
        'url': pkg_path,
        'md5': package['MD5sum'],
        'version': version,
        'release': release,
        'name': package['Package'],
        'arch': package['Architecture'],
        'size': package['Size'],
        'filename': os.path.basename('/' + package['Filename']),
    }
    return result

package_amd64 = get_package_info('/dists/stable/main/binary-amd64/Packages')
logger.debug("x64 package: {p}".format(p=package_amd64))
package_i686 = get_package_info('/dists/stable/main/binary-i386/Packages')
logger.debug("i686 package: {p}".format(p=package_i686))

logger.debug("Reading existing pkgbuild from: {p}".format(p=pkgbuild_name))
with open(pkgbuild_name, 'r') as fh:
    lines = fh.readlines()

output = ''
for line in lines:
    if line.startswith('source_x86_64='):
        line = 'source_x86_64=("{filename}::{url}")\n'.format(
            filename=package_amd64['filename'],
            url=package_amd64['url']
        )
    elif line.startswith('source_i686='):
        line = 'source_i686=("{filename}::{url}")\n'.format(
            filename=package_i686['filename'],
            url=package_i686['url']
        )
    elif line.startswith('md5sums_x86_64='):
        line = "md5sums_x86_64=('{m}')\n".format(m=package_amd64['md5'])
    elif line.startswith('md5sums_i686='):
        line = "md5sums_i686=('{m}')\n".format(m=package_i686['md5'])
    elif line.startswith('pkgver='):
        line = "pkgver={v}\n".format(v=package_amd64['version'])
    output += line

logger.info("Updated PKGBUILD:\n{o}".format(o=output))

logger.debug("Writing updated pkgbuild to: {p}".format(p=pkgbuild_name))
with open(pkgbuild_name, 'w') as fh:
    fh.write(output)
logger.info("Updated PKGBUILD written to disk.")
