#!/bin/bash

repo-add repo/jantman.db.tar.gz repo/*.pkg.tar.xz
~/venvs/foo/bin/s3cmd sync repo/* s3://archrepo.jasonantman.com/current/
# local symlink
~/venvs/foo/bin/s3cmd put repo/jantman.db.tar.gz s3://archrepo.jasonantman.com/current/jantman.db
