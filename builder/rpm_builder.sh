#!/bin/bash

cd src/

pyinstaller --clean --onefile -n zk-firma-digital -i zk-firma-digital/ui/ui_elements/images/icon.png --upx-dir=/usr/local/share/  --noconfirm --log-level=WARN --windowed --hidden-import 'pkcs11.defaults' main.py



DEB_HOMEDIR=~/rpmbuild/$NAME
mkdir -p $DEB_HOMEDIR
mkdir -p  ~/rpmbuild/$NAME/


cp dist/zk-firma-digital $DEB_HOMEDIR/zk-firma-digital.bin
cp ~/source/zk-firma-digital/ui/ui_elements/images/icon.png $DEB_HOMEDIR/icon.png
cp ~/source/os_libs/Athena/IDPClientDB.xml $DEB_HOMEDIR/zk-firma-digital_IDPClientDB.xml
cp ~/source/os_libs/linux/${ARCH}/libASEP11.so $DEB_HOMEDIR/libASEP11.so
cp ~/source/certs/ca_bundle.pem $DEB_HOMEDIR/

tee -a $DEB_HOMEDIR/zk-firma-digital.desktop << END
[Desktop Entry]
Name=ZK Firma Digital
Comment=Firma Digital para Costa Rica
Exec=/usr/share/zk-firma-digital/zk-firma-digital.bin
Icon=/usr/share/zk-firma-digital/icon.png
Terminal=false
Type=Application
Categories=Network;Application;
StartupNotify=true
END

cd ~/rpmbuild/
tar -zcf ~/rpmbuild/SOURCES/${NAME}-${VERSION}.tar.gz $NAME

sed -i 's/Name:           zk-firma-digital/Name:           '${NAME}'/g' SPECS/fva_client.spec
sed -i 's/Version:        0.2/Version:           '${VERSION}'/g' SPECS/fva_client.spec
rpmbuild -ba SPECS/fva_client.spec || exit 1

mv  ~/rpmbuild/RPMS/x86_64/${NAME}-${VERSION}-1.x86_64.rpm /packages/${NAME}-${VERSION}-1.${OS}.x86_64.rpm


