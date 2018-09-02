#! /bin/sh

#curl -L http://www.uu-world.cn/hxmt/hxmtsoft/linux/hxmtsoft.tar.gz > hxmtsoft_source_code.tar.gz
mkdir -p $ASTROPFX/hxmtsoft/

# COMPILING 
cd /home/hxmtsrc/ 
tar xvzf heasoft-6.24_hxmt.tar

cd /home/hxmtsrc/heasoft-6.24_hxmt/hxmt/BUILD_DIR/ && make clean
hmake clean
cd /home/hxmtsrc/heasoft-6.24_hxmt/BUILD_DIR/
./configure --prefix=$ASTROPFX/hxmtsoft/ --with-components="hxmt ftools"
make 
make install

rm -r heasoft-6.24_hxmt.tar
rm -rf heasoft-6.24
chmod -R g+rwx $ASTROPFX/hxmtsoft/
