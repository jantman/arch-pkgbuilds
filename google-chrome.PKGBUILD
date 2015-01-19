# Maintainer: Det <nimetonmaili g-mail>
# Contributors: t3ddy, Lex Rivera aka x-demon, ruario

# Check for new Linux releases in: http://googlechromereleases.blogspot.com/search/label/Stable%20updates
# or use: $ curl -s https://dl.google.com/linux/chrome/rpm/stable/x86_64/repodata/other.xml.gz | gzip -df | awk -F\" '/pkgid/{ sub(".*-","",$4); print $4": "$10 }'

pkgname=google-chrome
pkgver=39.0.2171.99
pkgrel=1
pkgdesc="An attempt at creating a safer, faster, and more stable browser (Stable Channel)"
arch=('i686' 'x86_64')
url="https://www.google.com/chrome/index.html"
license=('custom:chrome')
makedepends=('pacman>=4.2.0')
depends=('alsa-lib' 'desktop-file-utils' 'flac' 'gconf' 'gtk2' 'harfbuzz' 'harfbuzz-icu' 'hicolor-icon-theme'
         'icu' 'libpng' 'libxss' 'libxtst' 'nss' 'opus' 'snappy' 'speech-dispatcher' 'ttf-font' 'xdg-utils')
optdepends=('kdebase-kdialog: needed for file dialogs in KDE'
            'ttf-liberation: fix fonts for some PDFs')
provides=("google-chrome=$pkgver")
options=('!emptydirs' '!strip')
install=$pkgname.install
_channel=stable
source_x86_64=("google-chrome-${_channel}_${pkgver}_amd64.deb::https://dl.google.com/linux/direct/google-chrome-${_channel}_current_amd64.deb")
source_i686=("google-chrome-${_channel}_${pkgver}_i386.deb::https://dl.google.com/linux/direct/google-chrome-${_channel}_current_i386.deb")
source=('eula_text.html')
md5sums_x86_64=('037cef95bea64ffa87e926af59ae117b')
md5sums_i686=('b2e60863b171bfc152b25030df196ecb')
md5sums=('b7e752f549b215ac77f284b6486794b6')

package() {
  msg2 "Extracting the data.tar.lzma..."
  bsdtar -xf data.tar.lzma -C "$pkgdir/"

  msg2 "Moving stuff in place..."
  # Icons
  for i in 16 22 24 32 48 64 128 256; do
    install -Dm644 "$pkgdir"/opt/google/chrome/product_logo_$i.png \
                   "$pkgdir"/usr/share/icons/hicolor/${i}x$i/apps/google-chrome.png
  done

  # Man page
  gzip "$pkgdir"/usr/share/man/man1/google-chrome.1

  # License
  install -Dm644 eula_text.html "$pkgdir"/usr/share/licenses/google-chrome/eula_text.html

  msg2 "Symlinking missing Udev lib..."
  ln -s /usr/lib/libudev.so.1 "$pkgdir"/opt/google/chrome/libudev.so.0

  msg2 "Fixing Chrome icon resolution..."
  _name=$(echo ${source/_*} | sed 's/.*/\u&/')
  sed -i "/Exec=/i\StartupWMClass=$_name" "$pkgdir"/usr/share/applications/google-chrome.desktop

  msg2 "Fixing permissions of documentation folder..."
  chmod 755 "$pkgdir"/usr/share/doc/google-chrome-$_channel/

  msg2 "Adding support for CHROMIUM_USER_FLAGS..."
  sed -i 's/ "$@"/ $CHROMIUM_USER_FLAGS "$@"/' "$pkgdir"/opt/google/chrome/google-chrome

  msg2 "Removing unnecessities (e.g. Debian Cron job)..."
  rm -r "$pkgdir"/etc/cron.daily/ "$pkgdir"/opt/google/chrome/cron/
  rm "$pkgdir"/opt/google/chrome/product_logo_*.png
}
