#!/bin/bash

repo-add repo/jantman.db.tar.gz repo/*.pkg.tar.xz
~/venvs/foo/bin/s3cmd put -r repo/* s3://archrepo.jasonantman.com/current/
