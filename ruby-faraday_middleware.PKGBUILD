# Generated by gem2arch (https://github.com/anatol/gem2arch)
# Maintainer: Rhys Davies <rhys@johnguant.com>

_gemname=faraday_middleware
pkgname=ruby-$_gemname
pkgver=0.10.0
pkgrel=1
pkgdesc='Various middleware for Faraday'
arch=(any)
url='https://github.com/lostisland/faraday_middleware'
license=(MIT)
depends=(ruby ruby-faraday)
options=(!emptydirs)
source=(https://rubygems.org/downloads/$_gemname-$pkgver.gem)
noextract=($_gemname-$pkgver.gem)
sha1sums=('f9cce29c0aff6011f395610d6d2945a07910a84d')

package() {
  local _gemdir="$(ruby -e'puts Gem.default_dir')"
  gem install --ignore-dependencies --no-user-install -i "$pkgdir/$_gemdir" -n "$pkgdir/usr/bin" $_gemname-$pkgver.gem
  rm "$pkgdir/$_gemdir/cache/$_gemname-$pkgver.gem"
  install -D -m644 "$pkgdir/$_gemdir/gems/$_gemname-$pkgver/LICENSE.md" "$pkgdir/usr/share/licenses/$pkgname/LICENSE.md"
}