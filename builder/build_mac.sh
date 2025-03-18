 
#!/bin/zsh

set -xe

source /etc/profile
export LC_ALL="en_US.UTF-8"
VERSION='0.6.2'

cd src
pip install -r requirements.txt
pip install -r requirements-macos.txt
python setup.py py2app

mkdir -p dist/package/usr/local/zk-firma-digital/os_libs/macos
mkdir -p dist/package/usr/local/zk-firma-digital/CA-certificates
mkdir -p dist/package/usr/local/zk-firma-digital/etc/Athena
mkdir -p dist/package/usr/local/zk-firma-digital/zk-artifacts
mkdir -p dist/scripts

if [ ! -d dist/package/usr/local/zk-firma-digital/bin ];
then
    wget -qO- https://nodejs.org/dist/v22.12.0/node-v22.12.0-darwin-x64.tar.gz\
    | tar -xJf - --strip-components=1 -C dist/package/usr/local/zk-firma-digital
fi

cp -a dist/zk-firma-digital.app dist/package/usr/local/zk-firma-digital/
cp -a translations_en.qm dist/package/usr/local/zk-firma-digital/
cp spinner.gif dist/package/usr/local/zk-firma-digital/
cp -a CA-certificates/ dist/package/usr/local/zk-firma-digital/CA-certificates/
cp -a os_libs/macos/libASEP11.dylib dist/package/usr/local/zk-firma-digital/os_libs/macos/
cp -a os_libs/macos/libidop11.dylib dist/package/usr/local/zk-firma-digital/os_libs/macos/
cp -a os_libs/macos/libidolog.dylib dist/package/usr/local/zk-firma-digital/os_libs/macos/
cp -a os_libs/Athena/IDPClientDB.xml  dist/package/usr/local/zk-firma-digital/etc/Athena/
cp -a ../build/firma-verifier.zkey dist/package/usr/local/zk-firma-digital/zk-artifacts/firma-verifier.zkey
cp -a ../build/firma-verifier_js dist/package/usr/local/zk-firma-digital/zk-artifacts/firma-verifier_js
cp -a ../build/vkey.json dist/package/usr/local/zk-firma-digital/zk-artifacts/vkey.json

# Install snarkjs
if [ ! -d snarkjs_bundle ];
then
    mkdir -p snarkjs_bundle
    cd snarkjs_bundle
    npm init -y
    npm install snarkjs
    cd ..
fi

cp -a ./snarkjs_bundle/node_modules/ dist/package/usr/local/zk-firma-digital/lib/node_modules

if [ ! -e  dist/package/usr/local/zk-firma-digital/lib/snarkjs ];
then
    cd dist/package/usr/local/zk-firma-digital/lib
    ln -s node_modules/.bin/snarkjs snarkjs
    cd ../../../../../../
fi

tar -C dist/ -cf dist/package/usr/local/zk-firma-digital/zk-firma-digital.app.tar zk-firma-digital.app

tee dist/scripts/postinstall << END
#!/bin/sh
tar -C /Applications -xf /usr/local/zk-firma-digital/zk-firma-digital.app.tar
mv /Applications/zk-firma-digital.app  /Applications/zk-firma-digital.app
mkdir -p /etc/Athena/
cp /usr/local/zk-firma-digital/etc/Athena/IDPClientDB.xml /etc/Athena/

[ \! -e /usr/local/lib/libASEP11.dylib -o -L /usr/local/lib/libASEP11.dylib ] && cp \
    /usr/local/zk-firma-digital/os_libs/macos/libASEP11.dylib /usr/local/lib/libASEP11.dylib
[ \! -e /usr/local/lib/libidop11.dylib -o -L /usr/local/lib/libidop11.dylib ] && cp \
    /usr/local/zk-firma-digital/os_libs/macos/libidop11.dylib /usr/local/lib/libidop11.dylib
[ \! -e /usr/local/lib/libidolog.dylib -o -L /usr/local/lib/libidolog.dylib ] && cp \
    /usr/local/zk-firma-digital/os_libs/macos/libidolog.dylib /usr/local/lib/libidolog.dylib

exit 0 # all good
END
chmod u+x dist/scripts/postinstall

cd dist

pkgbuild --root ./package --identifier cr.zk-firma-digital  --script ./scripts --version 0.6.2 --install-location / ./zk-firma-digital.pkg

