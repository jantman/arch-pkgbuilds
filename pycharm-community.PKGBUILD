# Contributor: David Keogh <davekeogh@archlinux.us>

pkgname=pycharm-community
pkgver=4.5.2
pkgrel=1
pkgdesc="Powerful Python and Django IDE. Community edition."
arch=('any')
options=('!strip')
url="http://www.jetbrains.com/pycharm/"
license=('Apache')
depends=('java-environment>=6' 'giflib' 'ttf-font')
conflicts=('pycharm' 'pycharm-professional')
provides=('pycharm')
source=(http://download.jetbrains.com/python/$pkgname-$pkgver.tar.gz
        'pycharm-community.desktop' )
sha256sums=('a951141777a6581dfe7df0344abcb07406f43577913e56daf1010d6840b46127'
            '446134e5ef3012a6f19549d63fb3e18f07cdd00b39cd67fec99af9338a594f1e')

package() {
  cd $srcdir
  mkdir -p $pkgdir/opt/$pkgname
  cp -R $srcdir/$pkgname-$pkgver/* $pkgdir/opt/$pkgname
  
  if [[ $CARCH = 'i686' ]]; then
    rm -f $pkgdir/opt/$pkgname/bin/libyjpagent-linux64.so
    rm -f $pkgdir/opt/$pkgname/bin/fsnotifier64
    echo '-Dawt.useSystemAAFontSettings=on' >> $pkgdir/opt/$pkgname/bin/pycharm.vmoptions
    echo '-Dswing.aatext=true' >> $pkgdir/opt/$pkgname/bin/pycharm.vmoptions
  else
    echo '-Dawt.useSystemAAFontSettings=on' >> $pkgdir/opt/$pkgname/bin/pycharm64.vmoptions
    echo '-Dswing.aatext=true' >> $pkgdir/opt/$pkgname/bin/pycharm64.vmoptions 
  fi

  mkdir -p $pkgdir/usr/share/{applications,pixmaps}
  install -Dm644 $startdir/pycharm-community.desktop $pkgdir/usr/share/applications/
  install -Dm644 $pkgdir/opt/$pkgname/bin/pycharm.png $pkgdir/usr/share/pixmaps/pycharm.png
  
  mkdir -p $pkgdir/usr/bin
  ln -s /opt/pycharm-community/bin/pycharm.sh $pkgdir/usr/bin/pycharm
}

# vim:set ts=2 sw=2 et:
