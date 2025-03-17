#!/bin/bash -xe

set -xe

VERSION=0.6.3
NAME='zk-firma-digital'
PACKAGE='zk-firma-digital'
ARCH='amd64'

docker build -q -t debbuilder -f builder/Dockerfile_Debian .
# docker build -q -t rpmbuilder -f builder/Dockerfile_Fedora .
# docker build -q -t rpmbuildercentos -f builder/Dockerfile_Centos .
# mkdir -p rpm
mkdir -p deb
mkdir -p release

# chmod 777 rpm
chmod 777 deb

# docker run --rm --env VERSION=$VERSION --env NAME=$NAME --env ARCH=$ARCH  --env OS='centos' -v $(pwd)/rpm:/packages rpmbuildercentos
# docker run --rm --env VERSION=$VERSION --env NAME=$NAME --env ARCH=$ARCH  --env OS='fedora' -v $(pwd)/rpm:/packages rpmbuilder
docker run --rm --env VERSION=$VERSION --env NAME=$NAME --env ARCH=$ARCH --env PACKAGE=$PACKAGE -v $(pwd)/deb:/packages debbuilder

# cp rpm/* release/
cp deb/* release/
sha256sum release/*
