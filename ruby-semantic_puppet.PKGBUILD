# Maintainer: Jason Antman <jason@jasonantman.com>
_gemname=semantic_puppet
pkgname=ruby-$_gemname
pkgver=0.1.1
pkgrel=1
pkgdesc='Tools used by Puppet to parse, validate, and compare Semantic Versions and Version Ranges and to query and resolve module dependencies.'
arch=(any)
url='https://github.com/puppetlabs/semantic_puppet-gem'
license=('Apache')
depends=(
  'ruby'
)
source=(https://rubygems.org/downloads/$_gemname-$pkgver.gem)
noextract=($_gemname-$pkgver.gem)
sha256sums=('803dc62c61bbd7318197821590d8fe45f306ce8be4d1e54944ac7bfa1af2eff1')

package() {
  cd "$srcdir"
  # _gemdir is defined inside package() because if ruby[gems] is not installed on
  # the system, makepkg will exit with an error when sourcing the PKGBUILD.
  local _gemdir="$(ruby -rubygems -e'puts Gem.default_dir')"

  gem install --no-user-install --ignore-dependencies -i "$pkgdir$_gemdir" \
    -n "$pkgdir/usr/bin" "$_gemname-$pkgver.gem"
}
