#!/bin/bash -xe

rvm use system

for pkg in ruby-multipart-post ruby-faraday ruby-faraday_middleware ruby-multi_json ruby-faraday_middleware-multi_json ruby-colored ruby-cri ruby-semantic_puppet ruby-log4r ruby-minitar ruby-r10k
do
    if ls -1 ${pkg}*.pkg.tar.xz 2>&1 &>/dev/null; then
        echo "Package for $pkg already exists; not building"
        continue
    fi
    makepkg -p ${pkg}.PKGBUILD
done
