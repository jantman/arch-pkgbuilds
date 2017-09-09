#!/bin/bash -x

SCRIPTPATH=$(readlink -f $(dirname $0))

success=""
failed=""
for pkgname in bcwc-pcie-git facetimehd-firmware franz-bin google-chrome lastpass-cli-git macfanctld pycharm-community skype skypeforlinux-bin spotify vault-bin virtualbox-ext-oracle; do
  echo $pkgname
  cd $SCRIPTPATH
  ./aurget.sh $pkgname
done

for pkgname in bcwc-pcie-git facetimehd-firmware franz-bin google-chrome lastpass-cli-git macfanctld pycharm-community skype skypeforlinux-bin spotify vault-bin virtualbox-ext-oracle; do
  echo $pkgname
  cd "${SCRIPTPATH}/${pkgname}"
  if makepkg && rm -f ../repo/${pkgname}* && mv *.xz ../repo/; then
    success="${success} ${pkgname}"
  else
    failed="${failed} ${pkgname}"
  fi
done

echo "SUCCESSFULLY BUILT: $success"
echo "FAILED: $failed"
