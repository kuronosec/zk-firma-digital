#!/bin/bash

cp -a /zk_firma_digital_base /zk_firma_digital/
cd /zk_firma_digital/

pyinstaller --clean --onefile -n zk_firma_digital --upx-dir=/usr/local/share/  --noconfirm --log-level=WARN --windowed --distpath=/data/ --workpath=/tmp/zk_firma_digital_build --hidden-import 'pkcs11.defaults' main.py

mkdir -p /data/build/
cd  /data/build/

DEB_HOMEDIR="${PACKAGE}_${VERSION}_${ARCH}"
mkdir -p $DEB_HOMEDIR/usr/share/zk_firma_digital/os_libs/linux/${ARCH}/
mkdir -p $DEB_HOMEDIR/DEBIAN
mkdir -p $DEB_HOMEDIR/etc/Athena/
mkdir -p $DEB_HOMEDIR/usr/lib/x64-athena/
mkdir -p $DEB_HOMEDIR/usr/lib/${ARCH}-linux-gnu/
mkdir -p $DEB_HOMEDIR/usr/share/applications/
mkdir -p $DEB_HOMEDIR/usr/share/zk_firma_digital/zk_firma_digital/ui/ui_elements/images/

tee -a $DEB_HOMEDIR/DEBIAN/control << END
Package: ${PACKAGE}
Version: ${VERSION}
Architecture: ${ARCH}
Priority: optional
Section: non-free
Depends: pcscd, libxcb-xinerama0,  libxcb-util1 | libxcb-util0
Homepage: https://github.com/kuronosec/zk-firma-digital
Maintainer: Andrés Gómez Ramírez <andresgomezram7@gmail.com>
Description: Cliente para obtener credenciales de Zero-Knowledge basados en la Firma Digital de Costa Rica
 Cliente para obtener credenciales de Zero-Knowledge basados en la Firma Digital de Costa Rica
END

tee -a $DEB_HOMEDIR/usr/share/applications/zk_firma_digital.desktop << END
[Desktop Entry]
Name=Cliente FVA
Comment=Firma Digital para Costa Rica
Exec=/usr/share/zk_firma_digital/zk_firma_digital.bin
Terminal=false
Type=Application
Categories=Network;Application;
StartupNotify=true
END

cp /tmp/copyright $DEB_HOMEDIR/DEBIAN/
cp /tmp/postinst $DEB_HOMEDIR/DEBIAN/
sed -i 's/ARCH/'${ARCH}'/g' $DEB_HOMEDIR/DEBIAN/postinst
chmod 0775 $DEB_HOMEDIR/DEBIAN/postinst

cp /data/zk_firma_digital $DEB_HOMEDIR/usr/share/zk_firma_digital/zk_firma_digital.bin
cp /zk_firma_digital/os_libs/Athena/IDPClientDB.xml $DEB_HOMEDIR/etc/Athena/zk_firma_digital_IDPClientDB.xml
cp /zk_firma_digital/os_libs/linux/${ARCH}/libASEP11.so $DEB_HOMEDIR/usr/share/zk_firma_digital/os_libs/linux/${ARCH}/libASEP11.so
cp -a /zk_firma_digital/CA-certificates/ $DEB_HOMEDIR/usr/share/zk_firma_digital/

dpkg-deb --build --root-owner-group $DEB_HOMEDIR
alien -t $DEB_HOMEDIR.deb --scripts

cp $DEB_HOMEDIR.deb /packages
cp ${PACKAGE}-${VERSION}.tgz  /packages
chmod 777 /packages
