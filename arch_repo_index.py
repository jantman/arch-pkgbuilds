#!/usr/bin/env python
"""
Create an index.html file for the packages in an Arch Linux repo.

If you have ideas for improvements, or want the latest version, it's at:
<https://github.com/jantman/arch-pkgbuilds/blob/master/arch_repo_index.py>

Copyright 2016 Jason Antman <jason@jasonantman.com> <http://www.jasonantman.com>
Free for any use provided that patches are submitted back to me.

CHANGELOG:
2016-08-08 Jason Antman <jason@jasonantman.com>:
  - initial version of script
"""

import sys
import argparse
import logging
import tarfile
from platform import node as platform_node
from getpass import getuser
import pytz
import tzlocal
import os
from datetime import datetime
import subprocess

FORMAT = "[%(levelname)s %(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
logging.basicConfig(level=logging.ERROR, format=FORMAT)
logger = logging.getLogger(__name__)


class ArchRepoIndexer:
    """create index.html file for an Arch Package Repo"""

    def __init__(self, dbfile):
        """ init method, run at class creation """
        self.dbfile = dbfile

    def get_packages(self):
        """return a dict of package names in the repo to info about them"""
        logger.info('Reading repo db: %s', self.dbfile)
        pkgs = {}
        with tarfile.open(self.dbfile, 'r') as tf:
            for member in tf.getmembers():
                if not member.name.endswith('/desc'):
                    logger.debug('Skipping non-desc file: %s', member.name)
                    continue
                logger.debug('Extracting: %s', member.name)
                content = tf.extractfile(member).read().decode('utf-8')
                pkgs[member.name[:-5]] = self.info_for_package(content)
        logger.info('Got information for %d packages', len(pkgs))
        return pkgs

    def info_for_package(self, desc_content):
        """
        Given the content of a /desc file, return a dict of information
        about the package.
        """
        sections = {}
        in_sect = False
        curr_sect = []
        curr_name = ''
        for line in desc_content.split("\n"):
            line = line.strip()
            # end a section
            if line == '' and in_sect:
                if len(curr_sect) == 1:
                    curr_sect = curr_sect[0]
                sections[curr_name] = curr_sect
                logger.debug('End section %s: %s', curr_name, curr_sect)
                curr_name = None
                curr_sect = []
                in_sect = False
                continue
            if line.startswith('%') and not in_sect:
                curr_name = line.replace('%', '')
                in_sect = True
                continue
            if in_sect:
                curr_sect.append(line)
                continue
            if line != '':
                logger.error('Error parsing desc file; unknown line: %s', line)
        return sections

    def make_index_html(self, out_path, base_url=None):
        """generate the index.html file"""
        if base_url[-1] != '/':
            base_url = base_url + '/'
        packages = self.get_packages()
        pkhtml = self.make_package_html(packages, base_url)
        html = self.html_content(pkhtml, base_url)
        with open(out_path, 'w') as fh:
            fh.write(html)
        logger.warn('HTML written to: %s', out_path)

    def make_package_html(self, packages, base_url):
        """generate HTML table rows for packages"""
        h = ''
        for p in sorted(packages.keys()):
            data = packages[p]
            url = data['FILENAME']
            if base_url is not None:
                url = base_url + data['FILENAME']
            namelink = '<a href="%s">%s</a>' % (url, data['FILENAME'])
            h += "        <tr>\n"
            h += "          <td>%s</td>\n" % namelink
            h += "          <td>%s</td>\n" % data['NAME']
            h += "          <td>%s</td>\n" % data['VERSION']
            h += "          <td>%s</td>\n" % data['ARCH']
            builddate = datetime.fromtimestamp(
                int(data['BUILDDATE'])).strftime(
                    '%Y-%m-%d %H:%M:%S'
                )
            h += "          <td>%s</td>\n" % builddate
            h += "          <td>%s</td>\n" % data['DESC']
            h += "        </tr>\n"
        return h

    def make_base_snippet(self, base_url):
        if base_url is None:
            return ''
        reponame = os.path.basename(self.dbfile).split('.')[0]
        base_url_stripped = base_url
        if base_url[-1] == '/':
            base_url_stripped = base_url[:-1]
        s = """
    <p>This repository is hosted at: <a href="{base_url}">{base_url}</a>.
    You can add it to your system by adding the following snippet to
    <code>/etc/pacman.conf</code>:</p>
    <pre>
[{reponame}]
SigLevel = Optional TrustedOnly
Server = {base_url_stripped}
    </pre>
""".format(
    base_url=base_url,
    base_url_stripped=base_url_stripped,
    reponame=reponame
)
        return s

    def make_source_snippet(self):
        """attempt to generate a HTML snippet with the repo source"""
        path = os.path.dirname(os.path.abspath(os.path.expanduser(self.dbfile)))
        logger.debug('Repo path: %s', path)
        cmd = 'cd %s && git remote -v' % path
        try:
            logger.debug('Running: %s', cmd)
            res = subprocess.check_output(cmd, shell=True)
        except:
            logger.debug('Exception running: %s', cmd, exc_info=1)
            return ''
        logger.debug('Command output: %s', res)
        remotes = {}
        first_rmt = None
        for line in res.decode().split("\n"):
            line = line.strip()
            if line == '':
                continue
            parts = line.split()
            remotes[parts[0]] = parts[1]
            if first_rmt is None:
                first_rmt = parts[0]
        if len(remotes) < 1:
            return ''
        logger.debug('Repo git remotes: %s (first remote: %s)', remotes, first_rmt)
        if 'origin' in remotes:
            first_rmt = 'origin'
        return '    <p>Repository source: %s</p>' % remotes[first_rmt]

    def html_content(self, inner_content, base_url):
        """generate skeleton of HTML content"""
        title = 'Arch Repository Index'
        source_snippet = self.make_source_snippet()
        base_snippet = self.make_base_snippet(base_url)
        if base_url is not None:
            title = 'Arch Repository Index of %s' % base_url
        css = """
    <style>
    	table {
    		border:1px solid #C0C0C0;
    		border-collapse:collapse;
    		padding:5px;
    	}
    	th {
    		border:1px solid #C0C0C0;
    		padding:5px;
    		background:#F0F0F0;
    	}
    	td {
    		border:1px solid #C0C0C0;
    		padding:5px;
    	}
    </style>
"""
        c = """
<html>
  <head>
    <title>{title}</title>
{css}
  </head>
  <body>
    <h1>{title}</h1>
    <h2>Last Updated: {date}</h2>
{source_snippet}
{base_snippet}
    <table>
      <thead>
        <tr>
          <th>File</th>
          <th>Name</th>
          <th>Version</th>
          <th>Arch</th>
          <th>Build Date</th>
          <th>Description</th>
       </tr>
     </thead>
     </tbody>
{inner}
     </tbody>
    </table>
    <br />
    <hr />
    <p>Generated on {host} by {user} at {date}</p>
  </body>
</html>
""".format(
    inner=inner_content,
    title=title,
    date=datetime.now(pytz.utc).astimezone(
        tzlocal.get_localzone()).strftime('%Y-%m-%d %H:%M:%S%z %Z'),
    host=platform_node(),
    user=getuser(),
    base_snippet=base_snippet,
    css=css,
    source_snippet=source_snippet
    )
        return c


def parse_args(argv):
    """
    parse arguments/options
    """
    p = argparse.ArgumentParser(
        description='Create index.html for an Arch repo.'
    )
    p.add_argument('-b', '--base-url', dest='base_url', action='store',
                   type=str, default=None,
                   help='URL/path base for links; if not specified, will '
                        'create relative links')
    p.add_argument('-o', '--output-path', dest='out_path', action='store',
                   type=str, default='./index.html',
                   help='output path for HTML index; default: ./index.html')
    p.add_argument('-v', '--verbose', dest='verbose', action='count', default=0,
                   help='verbose output. specify twice for debug-level output.')
    p.add_argument('REPO_FILE_PATH', action='store', type=str,
                   help='path to <repo>.db[.tar[.gz]] file')
    args = p.parse_args(argv)
    return args

if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    if args.verbose > 1:
        logger.setLevel(logging.DEBUG)
    elif args.verbose > 0:
        logger.setLevel(logging.INFO)
    script = ArchRepoIndexer(args.REPO_FILE_PATH)
    script.make_index_html(args.out_path, base_url=args.base_url)
