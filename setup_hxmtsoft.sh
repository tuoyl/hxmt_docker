#! /bin/sh

cd $ASTROSOFT/hxmtsoft/source/
export hversion=2.06
echo `pwd`
echo `ls`

# careful about v_2.04 or v2.04
echo `ls`
gunzip hxmtsoftv${hversion}.tar.gz
tar -xvf hxmtsoftv${hversion}.tar
cd $ASTROSOFT/hxmtsoft/source/hxmtsoftv${hversion}/BUILD_DIR/

make clean
make distclean

export CC=$(command -v gcc)
export CXX=$(command -v g++)
export FC=$(command -v gfortran)

./configure --prefix=$ASTROSOFT/hxmtsoft/install/ --with-components="hxmt ftools "
make -j 4
make
make install
