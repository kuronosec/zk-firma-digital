#!/bin/bash

set -xe

VERSION=0.6.1

OLD_PATH=$(pwd)
echo $OLD_PATH

export PATH=$PATH:"C:\Program Files (x86)\Inno Setup 6"

mkdir -p build
cd src

# Create binary installer for the app
pyinstaller --clean --onefile -n zk-firma-digital --noconfirm \
    --log-level=WARN --windowed --icon=sakundi.ico --distpath=$OLD_PATH/build \
    --workpath=$OLD_PATH/build --noconsole main.py

cd $OLD_PATH/build
cp $OLD_PATH/builder/installer.iss $OLD_PATH/build
cp -r $OLD_PATH/src/CA-certificates $OLD_PATH/build

iscc installer.iss
mkdir -p $OLD_PATH/release/
cp Output/mysetup.exe $OLD_PATH/release/zk-firma-digital-$VERSION.exe
exit 0
