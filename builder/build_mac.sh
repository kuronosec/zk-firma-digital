 
#!/bin/zsh

set -xe

source /etc/profile
export LC_ALL="en_US.UTF-8"

cd src
pyinstaller zk-firma-digital.spec

mkdir -p dist/package/usr/local/zk-firma-digital/os_libs/macos
mkdir -p dist/package/usr/local/zk-firma-digital/CA-certificates
mkdir -p dist/package/usr/local/zk-firma-digital/etc/Athena
mkdir -p dist/package/usr/local/zk-firma-digital/zk-artifacts
mkdir -p dist/scripts

wget -qO- https://nodejs.org/dist/v22.12.0/node-v22.12.0-darwin-x64.tar.gz\
 | tar -xJf - --strip-components=1 -C dist/package/usr/local/zk-firma-digital

cp -a dist/zk-firma-digital.app dist/package/usr/local/zk-firma-digital/
cp -a CA-certificates/ dist/package/usr/local/zk-firma-digital/CA-certificates/
cp -a os_libs/macos/libASEP11.dylib dist/package/usr/local/zk-firma-digital/os_libs/macos/
cp -a os_libs/Athena/IDPClientDB.xml  dist/package/usr/local/zk-firma-digital/etc/Athena/
cp -a ../build/firma-verifier.zkey dist/package/usr/local/zk-firma-digital/zk-artifacts/firma-verifier.zkey
cp -a ../build/firma-verifier_js dist/package/usr/local/zk-firma-digital/zk-artifacts/firma-verifier_js
cp -a ../build/vkey.json dist/package/usr/local/zk-firma-digital/zk-artifacts/vkey.json
cp -R $(npm root -g)/snarkjs dist/package/usr/local/zk-firma-digital/lib/node_modules/

tar -C dist/ -cf dist/package/usr/local/zk-firma-digital/zk-firma-digital.app.tar zk-firma-digital.app

tee -a dist/scripts/postinstall << END
#!/bin/sh
tar -C /Applications -xf /usr/local/zk-firma-digital/zk-firma-digital.app.tar
mv /Applications/zk-firma-digital.app  /Applications/zk-firma-digital.app
mkdir -p /etc/Athena/
cp /usr/local/zk-firma-digital/etc/Athena/IDPClientDB.xml /etc/Athena/

[ \! -e /usr/local/lib/libASEP11.dylib -o -L /usr/local/lib/libASEP11.dylib ] && cp /usr/local/zk-firma-digital/os_libs/macos/libASEP11.dylib /usr/local/lib/libASEP11.dylib

exit 0 # all good
END
chmod u+x dist/scripts/postinstall

cd dist

pkgbuild --root ./package --identifier cr.zk-firma-digital  --script ./scripts --version 0.2 --install-location / ./zk-firma-digital.pkg

