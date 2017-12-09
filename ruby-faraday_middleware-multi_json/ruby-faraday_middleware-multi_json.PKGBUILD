# Maintainer: Jochen Schalanda <jochen+aur@schalanda.name>
_gemname=faraday_middleware-multi_json
pkgname=ruby-$_gemname
pkgver=0.0.6
pkgrel=1
pkgdesc='MultiJson parser for Faraday'
arch=('any')
url='https://github.com/denro/faraday_middleware-multi_json'
license=('MIT')
depends=('ruby' 'ruby-faraday_middleware' 'ruby-multi_json')
source=(http://rubygems.org/downloads/$_gemname-$pkgver.gem)
noextract=($_gemname-$pkgver.gem)
sha256sums=('38fc4dab7a78916ad09827d5a164aab62fbf2cb8b9de0507763de1f561d7a118')

package() {
  cd "$srcdir"
  local _gemdir="$(ruby -e'puts Gem.default_dir')"
  gem install --ignore-dependencies --no-user-install -i "$pkgdir$_gemdir" -n "$pkgdir/usr/bin" $_gemname-$pkgver.gem
}
