#!/bin/bash
# update-package-list.sh - Dump current repo contents to packages.list and commit
set -euo pipefail

REPO_NAME="jantman"

aur repo --database "$REPO_NAME" --list | sort > packages.list

if git diff --quiet packages.list 2>/dev/null; then
    echo "packages.list is already up to date."
else
    git add packages.list
    git commit -m "update packages.list"
    echo "packages.list updated and committed."
fi
