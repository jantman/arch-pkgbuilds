#!/bin/bash
# aur-prune.sh - Find and remove repo packages not installed on any machine
#
# Usage:
#   ./aur-prune.sh [pacman-Q-file ...]
#   ./aur-prune.sh --remove [pacman-Q-file ...]
#
# Compares packages in the jantman repo against installed packages on this
# machine (via pacman -Q) and optionally other machines (via files containing
# pacman -Q output). Packages not installed on ANY machine are candidates
# for removal.
#
# By default, only lists what would be removed (dry run). Pass --remove to
# actually remove packages.
#
# Examples:
#   # Dry run, this machine only
#   ./aur-prune.sh
#
#   # Dry run, this machine + two others
#   ./aur-prune.sh myprecious.txt othermachine.txt
#
#   # Actually remove, this machine + two others
#   ./aur-prune.sh --remove myprecious.txt othermachine.txt
#
# After removing, sync to S3 with: ./update_sync.sh
set -euo pipefail

REPO_NAME="jantman"
REPO_DIR="/home/jantman/GIT/arch-pkgbuilds/repo"
DRY_RUN=true

if [[ "${1:-}" == "--remove" ]]; then
    DRY_RUN=false
    shift
fi

# Collect installed package names from all machines
INSTALLED_PKGS=$(mktemp)
trap 'rm -f "$INSTALLED_PKGS"' EXIT

# This machine
pacman -Qq >> "$INSTALLED_PKGS"

# Additional machines from pacman -Q output files
for f in "$@"; do
    if [[ ! -f "$f" ]]; then
        echo "Error: file not found: $f" >&2
        exit 1
    fi
    # pacman -Q output is "pkgname version", extract just the name
    awk '{print $1}' "$f" >> "$INSTALLED_PKGS"
done

# Deduplicate
INSTALLED_PKGS_SORTED=$(mktemp)
trap 'rm -f "$INSTALLED_PKGS" "$INSTALLED_PKGS_SORTED"' EXIT
sort -u "$INSTALLED_PKGS" > "$INSTALLED_PKGS_SORTED"

# Get packages in our repo
REPO_PKGS=$(aur repo --database "$REPO_NAME" --list | awk '{print $1}')

# Find packages in repo but not installed anywhere
TO_REMOVE=()
for pkg in $REPO_PKGS; do
    if ! grep -qx "$pkg" "$INSTALLED_PKGS_SORTED"; then
        TO_REMOVE+=("$pkg")
    fi
done

if [[ ${#TO_REMOVE[@]} -eq 0 ]]; then
    echo "All repo packages are installed on at least one machine."
    exit 0
fi

echo "Packages in repo but not installed on any machine:"
for pkg in "${TO_REMOVE[@]}"; do
    echo "  $pkg"
done
echo ""
echo "${#TO_REMOVE[@]} package(s) to remove."

if $DRY_RUN; then
    echo ""
    echo "(dry run — no changes made)"
    exit 0
fi

echo ""
for pkg in "${TO_REMOVE[@]}"; do
    echo "Removing: $pkg"
    # Find the package file(s) in the repo directory
    pkg_files=$(find "$REPO_DIR" -name "${pkg}-*.pkg.tar.*" -not -name "*.sig" | while read -r f; do
        # Verify this file actually belongs to this package by checking
        # the filename pattern: pkgname-pkgver-pkgrel-arch.pkg.tar.*
        # or pkgname-epoch:pkgver-pkgrel-arch.pkg.tar.*
        basename "$f" | grep -qP "^\Q${pkg}\E-[^-]+-[^-]+-[^-]+\.pkg\.tar\." && echo "$f"
    done)
    if [[ -n "$pkg_files" ]]; then
        repo-remove "$REPO_DIR/jantman.db.tar.gz" "$pkg"
        for f in $pkg_files; do
            echo "  Deleting: $(basename "$f")"
            rm "$f"
        done
    else
        echo "  Warning: no package file found for $pkg, removing from DB only"
        repo-remove "$REPO_DIR/jantman.db.tar.gz" "$pkg"
    fi
done

echo ""
echo "=== Done ==="
echo "Run ./update_sync.sh to sync to S3."
