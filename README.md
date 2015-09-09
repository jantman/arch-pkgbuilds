# arch-pkgbuilds

[![Project Status: Active - The project has reached a stable, usable state and is being actively developed.](http://www.repostatus.org/badges/0.1.0/active.svg)](http://www.repostatus.org/#active)

My PKGBUILDs for Arch Linux

* __gcc43.PKGBUILD__ - gcc 4.3 from AUR
* __google-chrome.PKGBUILD__ - Google Chrome stable from [AUR](https://aur.archlinux.org/packages/google-chrome/)
* __packer-io-git.PKGBUILD__ - packer.io Git build
** __update_chrome.py__ - Python script to find the latest package version from the deb repository and update the PKGBUILD accordingly.
* __simulationcraft-git.PKGBUILD__ - my own PKGBUILD for [SimulationCraft](http://simulationcraft.org/) from git, based on the old [AUR simulationcraft-svn](https://aur.archlinux.org/packages/simulationcraft-svn/) one.
* __vmware-systemd-services.PKGBUILD__ - systemd services for VMWare Player / Workstation 11

## Building

1. ``makepkg -p filename.PKGBUILD``
2. ``mv *.pkg.tar.xz repo/``
3. ``./update_sync.sh`` to update the repo and sync to S3
