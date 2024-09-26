#!/bin/bash

sed -i 's/http:\/\/localhost:8000/https:\/\/firmadigital.solvosoft.com/g' source/zk_firma_digital/user_settings.py
sed -i 's/self.installation_path = None/self.installation_path = "\/usr\/share\/zk_firma_digital\/"/g'  source/zk_firma_digital/user_settings.py

cd source/

pyinstaller --clean --onefile -n zk_firma_digital -i zk_firma_digital/ui/ui_elements/images/icon.png --upx-dir=/usr/local/share/  --noconfirm --log-level=WARN --windowed --hidden-import 'pkcs11.defaults' main.py



DEB_HOMEDIR=~/rpmbuild/$NAME
mkdir -p $DEB_HOMEDIR
mkdir -p  ~/rpmbuild/$NAME/


cp dist/zk_firma_digital $DEB_HOMEDIR/zk_firma_digital.bin
cp ~/source/zk_firma_digital/ui/ui_elements/images/icon.png $DEB_HOMEDIR/icon.png
cp ~/source/os_libs/Athena/IDPClientDB.xml $DEB_HOMEDIR/zk_firma_digital_IDPClientDB.xml
cp ~/source/os_libs/linux/${ARCH}/libASEP11.so $DEB_HOMEDIR/libASEP11.so
cp ~/source/certs/ca_bundle.pem $DEB_HOMEDIR/

tee -a $DEB_HOMEDIR/zk_firma_digital.desktop << END
[Desktop Entry]
Name=Cliente FVA
Comment=Firma Digital para Costa Rica
Exec=/usr/share/zk_firma_digital/zk_firma_digital.bin
Icon=/usr/share/zk_firma_digital/icon.png
Terminal=false
Type=Application
Categories=Network;Application;
StartupNotify=true
END

cd ~/rpmbuild/
tar -zcf ~/rpmbuild/SOURCES/${NAME}-${VERSION}.tar.gz $NAME

sed -i 's/Name:           zk_firma_digital/Name:           '${NAME}'/g' SPECS/fva_client.spec
sed -i 's/Version:        0.2/Version:           '${VERSION}'/g' SPECS/fva_client.spec
rpmbuild -ba SPECS/fva_client.spec || exit 1

mv  ~/rpmbuild/RPMS/x86_64/${NAME}-${VERSION}-1.x86_64.rpm /packages/${NAME}-${VERSION}-1.${OS}.x86_64.rpm


