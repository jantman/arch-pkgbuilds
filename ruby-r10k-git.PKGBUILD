# Maintainer: Jason Antman <jason@jasonantman.com>
pkgname=ruby-r10k-git
pkgver=2.1.0dev.d5267e4
pkgrel=1
pkgdesc='Smarter Puppet deployment, powered by killer robots'
arch=(any)
url='https://github.com/puppetlabs/r10k'
license=('Apache')
depends=(
  'ruby'
  'ruby-colored>=1.2'
  'ruby-cri=2.6.1'
  'ruby-faraday>=0.9'
  'ruby-faraday_middleware=0.9.2'
  'ruby-faraday_middleware-multi_json>=0.0.6'
  'ruby-log4r>=1.1.10'
  'ruby-minitar'
  'ruby-multi_json>=1.10'
  'ruby-semantic_puppet>=0.1'
)
makedepends=('git')
conflicts=('ruby-r10k')
source=(
  "r10k"::"git+https://github.com/puppetlabs/r10k.git"
)
md5sums=(
  'SKIP'
)

pkgver() {
  cd "$srcdir/r10k"
  gemver=$(ruby -e 'load "lib/r10k/version.rb"; puts R10K::VERSION')
  gitref=$(git rev-parse --short HEAD)
  printf "%s.%s" $gemver $gitref
}

package() {
  cd "$srcdir/r10k"
  # _gemdir is defined inside package() because if ruby[gems] is not installed on
  # the system, makepkg will exit with an error when sourcing the PKGBUILD.
  local _gemdir="$(ruby -rubygems -e'puts Gem.default_dir')"

  gem build r10k.gemspec
  gemver=$(ruby -e 'load "lib/r10k/version.rb"; puts R10K::VERSION')
  gem install --no-user-install --ignore-dependencies -i "$pkgdir$_gemdir" \
    -n "$pkgdir/usr/bin" "r10k-$gemver.gem"
}
