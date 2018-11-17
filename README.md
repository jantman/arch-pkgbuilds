# arch-pkgbuilds

[![Project Status: Active - The project has reached a stable, usable state and is being actively developed.](http://www.repostatus.org/badges/0.1.0/active.svg)](http://www.repostatus.org/#active)

My PKGBUILDs for Arch Linux

## Grabbing New Packages

``./aurget.sh PKG-NAME``

## Rebuilding / Updating

1. ``export BASEREV=$(git rev-parse HEAD)``
2. ``python3 rebuild.py -v repo/jantman.db.tar.gz``
3. Verify the changes look acceptable: ``git diff $BASEREV HEAD``
4. Assuming everything looks right, update the repo and sync to S3: ``./update_sync.sh``
