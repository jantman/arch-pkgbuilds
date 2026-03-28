#!/bin/bash
# aur-rebuild.sh - Check for AUR updates and library rebuilds
# Replaces rebuild.py using aurutils + rebuild-detector
#
# Usage:
#   ./aur-rebuild.sh              # Check for updates and build them
#   ./aur-rebuild.sh --dry-run    # Show what needs updating without building
#   ./aur-rebuild.sh --force PKG  # Force rebuild a specific package
#
# After running, sync to S3 with: ./update_sync.sh
set -euo pipefail

REPO_NAME="jantman"

# Packages to ignore (equivalent to IGNORE_PACKAGES in rebuild.py)
IGNORE_PACKAGES=(
    lego-git
    brother-mfc-j5945dw
    python-ajsonrpc
)

# Build --ignore arguments for aur sync
IGNORE_ARGS=()
for pkg in "${IGNORE_PACKAGES[@]}"; do
    IGNORE_ARGS+=("--ignore=$pkg")
done

if [[ "${1:-}" == "--dry-run" ]]; then
    echo "=== AUR packages with available updates ==="
    aur repo --database "$REPO_NAME" --upgrades "${IGNORE_ARGS[@]}" || true
    echo ""
    echo "=== Packages needing library rebuilds ==="
    checkrebuild | awk -v repo="$REPO_NAME" '$1 == repo' || true
    exit 0
fi

if [[ "${1:-}" == "--force" ]]; then
    shift
    if [[ $# -eq 0 ]]; then
        echo "Usage: $0 --force <package-name> [<package-name> ...]" >&2
        exit 1
    fi
    echo "=== Force rebuilding: $* ==="
    aur sync --database "$REPO_NAME" --no-view --no-confirm --force "$@"
    echo ""
    echo "Done. Run ./update_sync.sh to sync to S3."
    exit 0
fi

# --- Step 1: Check and build AUR updates ---
echo "=== Checking for AUR updates ==="
aur sync --database "$REPO_NAME" --upgrades --no-view --no-confirm "${IGNORE_ARGS[@]}" "$@"

# --- Step 2: Check for library rebuilds ---
echo ""
echo "=== Checking for packages needing library rebuilds ==="
REBUILD_LIST=$(checkrebuild | awk -v repo="$REPO_NAME" '$1 == repo {print $2}' || true)

if [[ -n "$REBUILD_LIST" ]]; then
    echo "Packages needing rebuild:"
    echo "$REBUILD_LIST"
    echo ""
    for pkg in $REBUILD_LIST; do
        # Skip ignored packages
        skip=false
        for ignored in "${IGNORE_PACKAGES[@]}"; do
            if [[ "$pkg" == "$ignored" ]]; then
                skip=true
                break
            fi
        done
        if $skip; then
            echo "Skipping ignored package: $pkg"
            continue
        fi
        echo "Rebuilding: $pkg"
        aur sync --database "$REPO_NAME" --no-view --no-confirm --force "$pkg"
    done
else
    echo "No packages need library rebuilds."
fi

echo ""
echo "=== Done ==="
echo "Run ./update_sync.sh to sync to S3."
