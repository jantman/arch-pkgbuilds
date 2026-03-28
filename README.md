# arch-pkgbuilds

[![Project Status: Active - The project has reached a stable, usable state and is being actively developed.](http://www.repostatus.org/badges/0.1.0/active.svg)](http://www.repostatus.org/#active)

**Repository Index: http://archrepo.jasonantman.com/current/**

My PKGBUILDs for Arch Linux

## Grabbing New Packages

``./aurget.sh PKG-NAME``

## Rebuilding / Updating

1. ``export BASEREV=$(git rev-parse HEAD)``
2. ``python3 rebuild.py -v repo/jantman.db.tar.gz``
3. Verify the changes look acceptable: ``git diff $BASEREV HEAD``
4. Assuming everything looks right, update the repo and sync to S3: ``./update_sync.sh``

## Future Enhancement

See [github_actions_process.md](github_actions_process.md) for a design document on moving to GitHub Actions-based builds with S3 hosting. See also [repo_overhaul.md](repo_overhaul.md) for a broader comparison of options.
