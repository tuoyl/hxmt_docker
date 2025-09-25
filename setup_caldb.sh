#! /bin/sh                                                                                                                                                                                                                                

export caldbversion=2.07

cd $ASTROSOFT/hxmtsoft/
gunzip CALDB${caldbversion}.tar.gz
tar -xvf CALDB${caldbversion}.tar
mv CALDB${caldbversion} CALDB
