#! /bin/sh

cd $ASTROSOFT/hxmtsoft/
echo `ls`
wget -O CALDB.tar.gz  http://www.hxmt.cn/u/cms/enwww/202003/CALDB2.02.tar.gz
echo `ls`
gunzip CALDB.tar.gz
tar -xvf CALDB.tar
cd $ASTROSOFT/hxmtsoft/CALDB
