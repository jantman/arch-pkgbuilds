# arch-pkgbuilds

[![Project Status: Active - The project has reached a stable, usable state and is being actively developed.](http://www.repostatus.org/badges/0.1.0/active.svg)](http://www.repostatus.org/#active)

**Repository Index: http://archrepo.jasonantman.com/current/**

Personal AUR package repository for Arch Linux, managed with
[aurutils](https://github.com/aurutils/aurutils) and
[rebuild-detector](https://github.com/maximbaz/rebuild-detector).

## Prerequisites

On the build machine (phoenix):
- `aurutils` and `rebuild-detector` installed (managed by Puppet via `phoenix_packages.pp`)
- `[jantman]` repo in `/etc/pacman.conf` with `Server = file:///home/jantman/GIT/arch-pkgbuilds/repo` (managed by Puppet via `archlinux_base.pp`)

On other machines:
- `[jantman]` repo in `/etc/pacman.conf` with `Server = http://archrepo.jasonantman.com/current` (managed by Puppet)

## Adding a New Package

```bash
# Build and add to the local repo (shows PKGBUILD diff for review)
aur sync --database jantman <package-name>

# Sync to S3
./update_sync.sh
```

`aur sync` fetches the PKGBUILD from AUR, shows a diff for review,
builds, and adds the package to the local repo. aurutils maintains
its own git clones (with full history) in `~/.cache/aurutils/sync/`.

## Checking for Updates and Rebuilding

```bash
# Dry run - show what needs updating
./aur-rebuild.sh --dry-run

# Build all updates + library rebuilds
./aur-rebuild.sh

# Force rebuild a specific package
./aur-rebuild.sh --force <package-name>

# Sync to S3
./update_sync.sh
```

## Checking for Library Rebuilds

After system updates, check for packages linked against outdated libraries:

```bash
checkrebuild -i jantman
```

This is also run automatically as part of `./aur-rebuild.sh`.

## Pruning Unused Packages

Find and remove repo packages that aren't installed on any machine:

```bash
# Dry run (default) - this machine only
./aur-prune.sh

# Dry run - this machine + others (pass pacman -Q output files)
./aur-prune.sh myprecious.txt othermachine.txt

# Actually remove
./aur-prune.sh --remove myprecious.txt othermachine.txt

# Sync to S3
./update_sync.sh
```

To generate a package list on a remote machine: `pacman -Q > hostname.txt`,
then SCP the file to phoenix.

## Ignored Packages

Some packages are excluded from automatic updates (see the `IGNORE_PACKAGES`
list in `aur-rebuild.sh`). These must be built/updated manually.

## Legacy

- `rebuild.py` - replaced by `aur-rebuild.sh` (uses aurutils)
- `aurget.sh` - replaced by `aur sync --database jantman <pkg>`
- `*/PKGBUILD` directories - historical snapshots; no longer updated.
  aurutils tracks PKGBUILDs (with full git history) in `~/.cache/aurutils/sync/`

## Future Enhancements

### Automation (systemd timers)

The current workflow is manual. Future automation options:

- **Semi-automated:** Systemd timer on phoenix runs `aur sync --upgrades` daily
  and builds updates automatically. S3 sync stays manual for review before
  pushing to all machines.
- **Fully automated:** Timer runs `aur-rebuild.sh` + `update_sync.sh` on a
  schedule. All 3 machines get updates automatically.
- **Pacman hook for rebuild-detector:** Run `checkrebuild` automatically after
  every `pacman -Syu` on phoenix to catch library-triggered rebuilds immediately.

### GitHub Actions

See [github_actions_process.md](github_actions_process.md) for a design document
on moving to GitHub Actions-based builds with S3 hosting.
