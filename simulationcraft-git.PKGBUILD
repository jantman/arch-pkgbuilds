# Maintainer: Jason Antman <jason@jasonantman.com>
pkgname="simulationcraft-git"
pkgdesc="A tool to simulate, analyze, and graphically display World of Warcraft combat (GIT code, CLI only)"
pkgver=603.23.1.g555b62b
pkgrel=1
arch=('x86_64')
url="https://code.google.com/p/simulationcraft/"
license=('GPL3')
depends=('gcc-libs')
makedepends=('git' 'gcc')
source=('git+https://code.google.com/p/simulationcraft/')
md5sums=('SKIP')
_gitname=simulationcraft

pkgver () {
  cd $_gitname
  echo $(git describe --tags --always | sed 's/^release-//' | sed 's/-/./g')
}

prepare() {
  msg2 "Starting prepare in: `pwd`"
  cd $_gitname
  git checkout master
  git fetch
  git pull
  cd engine
  make clean
}

build() {
  cd $_gitname/engine
  make
}

package () {
  cd $_gitname/engine
  install -Dm755 simc "$pkgdir"/usr/bin/simc
}

# vim:set ts=4 sw=4 et:
