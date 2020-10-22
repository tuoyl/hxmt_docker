#! /bin/sh

cd $ASTROSOFT/hxmtsoft/source/
export hversion=2.02
echo `pwd`
echo `ls`
wget -O hxmtsoft_v$hversion.tar.gz  http://www.hxmt.cn/u/cms/enwww/202003/hxmtsoftv2.02.tar.gz
echo `ls`
gunzip hxmtsoft_v$hversion.tar.gz
tar -xvf hxmtsoft_v$hversion.tar
cd $ASTROSOFT/hxmtsoft/source/hxmtsoftv$hversion/BUILD_DIR/
make clean
make distclean
./configure --prefix=$ASTROSOFT/hxmtsoft/install/
make
make install
