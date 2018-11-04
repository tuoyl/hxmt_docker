#!/bin/bash

# docker setup script for MacOS 

#set -xe

echo "HXMT_VERSION == ${HXMT_VERSION:=latest}"
echo "HXMT_DOCKER_IMAGE == ${HXMT_DOCKER_IMAGE:=ihepuni/hxmtsoft:${HXMT_VERSION}}"
echo "HXMT_DOCKER_PULL == \"${HXMT_DOCKER_PULL:=yes}\""
echo "DATA_DIRECTORY == ${DATA_DIRECTORY:=`pwd`}"
[ "$HXMT_DOCKER_PULL" ==  "yes" ] && {
    echo "will update image (set HXMT_DOCKER_PULL to anything but \"yes\" to stop this)"
    docker pull $HXMT_DOCKER_IMAGE
}

[ -s /tmp/.X11-unix ] || { echo "no /tmp/.X11-unix? no X? not allowed!"; }

echo ""
echo " ------ container initialized ------ "
echo ""

xhost + 127.0.0.1 && \
docker run \
    -it --init --rm \
    -e HOST_USER_ID=`id -u $USER` \
    -e DISPLAY=docker.for.mac.localhost:0 \
    -v $DATA_DIRECTORY:/data \
    ${HXMT_DOCKER_IMAGE}
