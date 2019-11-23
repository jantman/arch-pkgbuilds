#!/bin/bash -ex

repo-add -R -n repo/jantman.db.tar.gz repo/*.pkg.tar.xz
source ~/venvs/current/bin/activate
python arch_repo_index.py -vv -b http://archrepo.jasonantman.com/current/ -o repo/index.html repo/jantman.db.tar.gz
~/bin/aws s3 sync repo s3://archrepo.jasonantman.com/current/ --delete
# local symlink
~/bin/aws s3 cp repo/jantman.db.tar.gz s3://archrepo.jasonantman.com/current/jantman.db

echo "WARNING: because Arch doesn't really support versioning, you can only have one version of a given package in a repo at a time. 'repo-add' will remove the old version before adding a new one. Unfortunately, it doesn't seem to have any version comparison logic; using '*' here will add packages in lexicographic order, so if we have both foo-1.2.2 and foo-1.2.12 in the source directory, 'foo-1.2.2' will win. Yuck."
