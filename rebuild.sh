#!/bin/bash -x

SCRIPTPATH=$(readlink -f $(dirname $0))
PKGNAMES="chromedriver google-chrome hotshots macfanctld spotify virtualbox-ext-oracle"

success=""
failed=""
for pkgname in $PKGNAMES; do
  echo $pkgname
  cd $SCRIPTPATH
  ./aurget.sh $pkgname
done

for pkgname in $PKGNAMES; do
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
