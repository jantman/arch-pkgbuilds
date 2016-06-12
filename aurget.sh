#!/bin/bash -x
# aurget - pull down an AUR package and add it to my git repo

packagename=$1
dest_dir=$packagename
[[ -d $dest_dir ]] && rm -Rf $dest_dir
mkdir $dest_dir
git clone --depth=1 "https://aur.archlinux.org/${packagename}.git" $dest_dir
pushd $dest_dir
gitrev=$(git rev-parse HEAD)
read -p "Opening PKGBUILD with less. Please inspect for any malicious code."
unset LESS
unset LESSOPEN
less PKGBUILD
read -p "Ctrl+C now to exit, or continue to source PKGBUILD and get vars"
pkgver=`source PKGBUILD && echo "\${pkgver}-\${pkgrel}"`
rm -Rf .git
popd
git add $dest_dir
git commit -m "aurget.sh - pull in ${packagename}-${pkgver} from AUR at commit ${gitrev}"
