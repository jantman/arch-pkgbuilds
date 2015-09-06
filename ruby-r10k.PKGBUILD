# Maintainer: Jason Antman <jason@jasonantman.com>
_gemname=r10k
pkgname=ruby-$_gemname
pkgver=2.0.3
pkgrel=1
pkgdesc='Smarter Puppet deployment, powered by killer robots'
arch=(any)
url='https://github.com/puppetlabs/r10k'
license=('Apache')
depends=(
  'ruby'
  'ruby-colored>=1.2'
  'ruby-cri>=2.6.1'
  'ruby-faraday>=0.9'
  'ruby-faraday_middleware>=0.9'
  'ruby-faraday_middleware-multi_json>=0.0.6'
  'ruby-log4r>=1.1.10'
  'ruby-minitar'
  'ruby-multi_json>=1.10'
  'ruby-semantic_puppet>=0.1'
)
source=(https://rubygems.org/downloads/$_gemname-$pkgver.gem)
noextract=($_gemname-$pkgver.gem)
sha256sums=('ef28c179d30c6908021320ae835cb4431ed939423369853b2d890de2ffea54f8')

package() {
  cd "$srcdir"
  # _gemdir is defined inside package() because if ruby[gems] is not installed on
  # the system, makepkg will exit with an error when sourcing the PKGBUILD.
  local _gemdir="$(ruby -rubygems -e'puts Gem.default_dir')"

  gem install --no-user-install --ignore-dependencies -i "$pkgdir$_gemdir" \
    -n "$pkgdir/usr/bin" "$_gemname-$pkgver.gem"
}
