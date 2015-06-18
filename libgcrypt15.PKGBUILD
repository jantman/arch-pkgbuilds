# Maintainer: "UnCO" Lin <trash__box <_at_> 163.com>
# Contributor: Andreas Radke <andyrtr <_at_> archlinux.org>

pkgname=libgcrypt15
_pkgname=libgcrypt
pkgver=1.5.4
_apiver=11.8.3
pkgrel=4
pkgdesc="General purpose cryptographic library based on the code from GnuPG"
arch=(any)
url="http://www.gnupg.org"
license=('LGPL')
depends=()
source=(
  ftp://ftp.gnupg.org/gcrypt/${_pkgname}/${_pkgname}-${pkgver}.tar.bz2
  # HTTP MIRRORS
  # http://gd.tuwien.ac.at/privacy/gnupg/${_pkgname}/${_pkgname}-${pkgver}.tar.bz2
  # http://artfiles.org/gnupg.org/${_pkgname}/${_pkgname}-${pkgver}.tar.bz2
  # http://ftp.heanet.ie/mirrors/ftp.gnupg.org/gcrypt/${_pkgname}/${_pkgname}-${pkgver}.tar.bz2
  # http://www.mirrorservice.org/sites/ftp.gnupg.org/gcrypt/${_pkgname}/${_pkgname}-${pkgver}.tar.bz2
  # http://www.ring.gr.jp/pub/net/gnupg/${_pkgname}/${_pkgname}-${pkgver}.tar.bz2
  #
  # Currently, this mirror returns 403
  # http://mirrors.dotsrc.org/gcrypt/${_pkgname}/${_pkgname}-${pkgver}.tar.bz2
  debian_security_patches.patch
)
sha1sums=('bdf4b04a0d2aabc04ab3564fbe38fd094135aa7a'
          'eb1b1c3a8afd6705573455b9259ac6ece961d1b3')

prepare() {
  cd ${_pkgname}-${pkgver}
  patch -Np1 -i "$srcdir"/debian_security_patches.patch
}

build() {
  cd ${_pkgname}-${pkgver}
  ./configure --prefix=/usr \
    --disable-static \
    --disable-padlock-support
  make
}

# check() {
  # cd ${_pkgname}-${pkgver}
  # make check
# }

package() {
  cd ${_pkgname}-${pkgver}
  install -Dm755 src/.libs/libgcrypt.so.${_apiver} "$pkgdir/usr/lib/libgcrypt.so.${_apiver}"
  cd "$pkgdir/usr/lib"
  ln -s libgcrypt.so.${_apiver} libgcrypt.so.11
}
