#! /bin/sh

cd $ASTROSOFT/hxmtsoft/
echo `ls`
wget -O CALDB.tar.gz  http://www.hxmt.cn/u/cms/www/202011/CALDB2.04.tar.gz
echo `ls`
gunzip CALDB.tar.gz
tar -xvf CALDB.tar
mv CALDB2.04 CALDB
