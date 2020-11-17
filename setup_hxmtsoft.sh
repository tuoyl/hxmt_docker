#! /bin/sh

cd $ASTROSOFT/hxmtsoft/source/
export hversion=2.04
echo `pwd`
echo `ls`
# careful about v_2.04 or v2.04
wget -O hxmtsoftv$hversion.tar.gz http://www.hxmt.cn/u/cms/www/202011/hxmtsoftv2.04.tar.gz
echo `ls`
gunzip hxmtsoftv$hversion.tar.gz
tar -xvf hxmtsoftv$hversion.tar
cd $ASTROSOFT/hxmtsoft/source/hxmtsoftv$hversion/BUILD_DIR/
#cd $ASTROSOFT/hxmtsoft/source/BUILD_DIR/
make clean
make distclean

# fix gcc-gfortran version too old problem
yum -y install centos-release-scl
yum -y  install devtoolset-7-gcc*
scl enable devtoolset-7 bash

export CC=/opt/rh/devtoolset-7/root/usr/bin/gcc
export CXX=/opt/rh/devtoolset-7/root/usr/bin/g++
export FC=/opt/rh/devtoolset-7/root/usr/bin/gfortran
export PERL=/usr/bin/perl
./configure --prefix=$ASTROSOFT/hxmtsoft/install/ --with-components="heacore tcltk attitude heasptools heatools heagen demo hxmt Xspec ftools "
make
make install
