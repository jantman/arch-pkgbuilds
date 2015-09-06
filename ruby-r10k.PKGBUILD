# Maintainer: Jochen Schalanda <jochen+aur@schalanda.name>
_gemname=r10k
pkgname=ruby-$_gemname
pkgver=1.3.2
pkgrel=1
pkgdesc='Smarter Puppet deployment, powered by killer robots'
arch=(any)
url='http://github.com/adrienthebo/r10k'
license=('Apache')
depends=(
  'ruby'
  'ruby-colored>=1.2'
  'ruby-cri>=2.5.0'
  'ruby-systemu-2.5'
  'ruby-log4r>=1.1.10'
  'ruby-multi_json-1.8'
  'ruby-json_pure'
  'ruby-faraday-0.8'
  'ruby-faraday_middleware'
  'ruby-faraday_middleware-multi_json')
source=(https://rubygems.org/downloads/$_gemname-$pkgver.gem)
noextract=($_gemname-$pkgver.gem)
sha256sums=('d087711e3dd36aace9be2927fd525066d134e5ab19b60c62c2daabf67357ecbd')

package() {
  cd "$srcdir"
  # _gemdir is defined inside package() because if ruby[gems] is not installed on
  # the system, makepkg will exit with an error when sourcing the PKGBUILD.
  local _gemdir="$(ruby -rubygems -e'puts Gem.default_dir')"

  gem install --no-user-install --ignore-dependencies -i "$pkgdir$_gemdir" \
    -n "$pkgdir/usr/bin" "$_gemname-$pkgver.gem"
}
