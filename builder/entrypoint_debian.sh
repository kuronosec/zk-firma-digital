#!/bin/bash

# Copy source code files
cp -a /zk-firma-digital_base /zk-firma-digital/
cd /zk-firma-digital/

# Create binary installer for the app
pyinstaller --clean --onefile -n zk-firma-digital --upx-dir=/usr/local/share/  \
    --noconfirm --log-level=WARN --windowed --distpath=/data/ \
    --workpath=/tmp/zk-firma-digital_build main.py

mkdir -p /data/build/
cd  /data/build/

# Create installation directory
DEB_HOMEDIR="${PACKAGE}_${VERSION}_${ARCH}"
mkdir -p $DEB_HOMEDIR/usr/share/zk-firma-digital/os_libs/linux/${ARCH}/
mkdir -p $DEB_HOMEDIR/DEBIAN
mkdir -p $DEB_HOMEDIR/etc/Athena/
mkdir -p $DEB_HOMEDIR/usr/lib/x64-athena/
mkdir -p $DEB_HOMEDIR/usr/lib/${ARCH}-linux-gnu/
mkdir -p $DEB_HOMEDIR/usr/share/applications/
mkdir -p $DEB_HOMEDIR/usr/share/zk-firma-digital/zk-artifacts

# Provide information about the package

tee -a $DEB_HOMEDIR/DEBIAN/control << END
Package: ${PACKAGE}
Version: ${VERSION}
Architecture: ${ARCH}
Priority: optional
Section: non-free
Depends: pcscd, libxcb-xinerama0,  libxcb-util1 | libxcb-util0, libccid, libpcre3, npm, nodejs
Homepage: https://github.com/kuronosec/zk-firma-digital
Maintainer: Andrés Gómez Ramírez <andresgomezram7@gmail.com>
Description: Cliente para obtener credenciales de Zero-Knowledge basados
  en la Firma Digital de Costa Rica Cliente para obtener credenciales de
  Zero-Knowledge basados en la Firma Digital de Costa Rica
END

# Create Descktop Launcher

tee -a $DEB_HOMEDIR/usr/share/applications/zk-firma-digital.desktop << END
[Desktop Entry]
Name=ZK Firma Digital
Comment=Firma Digital para Costa Rica
Exec=/usr/share/zk-firma-digital/zk-firma-digital.bin %u
Terminal=false
Type=Application
Categories=Network;Application;
StartupNotify=true
MimeType=x-scheme-handler/zk-firma-digital;
END

# Add copyright and post installation script
cp /tmp/copyright $DEB_HOMEDIR/DEBIAN/
cp /tmp/postinst $DEB_HOMEDIR/DEBIAN/
sed -i 's/ARCH/'${ARCH}'/g' $DEB_HOMEDIR/DEBIAN/postinst
chmod 0775 $DEB_HOMEDIR/DEBIAN/postinst

# Actually copy application data to the end directories
cp /data/zk-firma-digital $DEB_HOMEDIR/usr/share/zk-firma-digital/zk-firma-digital.bin
cp /zk-firma-digital/os_libs/Athena/IDPClientDB.xml $DEB_HOMEDIR/etc/Athena/zk-firma-digital_IDPClientDB.xml
cp /zk-firma-digital/os_libs/linux/${ARCH}/libASEP11.so \
    $DEB_HOMEDIR/usr/share/zk-firma-digital/os_libs/linux/${ARCH}/libASEP11.so
cp -a /zk-firma-digital/CA-certificates/ $DEB_HOMEDIR/usr/share/zk-firma-digital/
cp -a /zk-artifacts/firma-verifier_js $DEB_HOMEDIR/usr/share/zk-firma-digital/zk-artifacts
cp -a /zk-artifacts/vkey.json $DEB_HOMEDIR/usr/share/zk-firma-digital/zk-artifacts
cp -a /zk-artifacts/firma-verifier.zkey $DEB_HOMEDIR/usr/share/zk-firma-digital/zk-artifacts

dpkg-deb --build --root-owner-group $DEB_HOMEDIR
alien -t $DEB_HOMEDIR.deb --scripts

cp $DEB_HOMEDIR.deb /packages
cp ${PACKAGE}-${VERSION}.tgz  /packages
chmod 777 /packages
