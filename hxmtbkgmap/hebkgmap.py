#!/usr/bin/env python
'''
Model constructed by Background Group.
Lian Jinyuan, Zhangshu, Guo Chengcheng et al.
Mail liaojinyuan@ihep.ac.cn

'''
'''
This version was written by Ge Mingyu
Mail gemy@ihep.ac.cn

Usage:

hebkgmap lc/spec blind_det.FITS ehkfile.fits gtifile.fits deadtime.fits lcname/specname outnam_prefix (spec_time_arnge)
    lc/spec: lc for background lightcurve and spec for background light curve 
    blind_det_events.FITS: should only include the events for blind detecters.
    ehkfile.fits: the EHK file for the observation
    gtifile.fits: the GTI file for ME
    deadtime.fits: the Dead Time for ME
    lcname/specname: is ASCII file, which includes the name of the source file for small FOV
    chmin: minimum channel for light curve
    chmax: maximum channel for light curve
    outnam_prefix: the output prefix for the spectrum

Using interactive method in prompt.	

'''

from astropy.io import fits as pf
import numpy as np
import matplotlib.pyplot as plt
import os
import commands
import sys
import time

Ver = '2.0.5'

print "*********************************************************"
print "******************  Running HXMT Bkg   ******************"
print "*********************************************************"
print "*********************************************************"
print "*********************************************************"
print "************ PRINT: hebkgmap -h for usage   *************"
print "*********************************************************"
print "HXMT background for Insight-HXMT/HE, ver-",Ver

uage_method1 = 'Method 1: hebkgmap lc/spec blind_det16.FITS ehkfile.fits gtifile.fits deadtime.fits lcname/specname chmin chmax outnam_prefix (spec_time_arnge)'
uage_method2 = 'Method 2: Using interactive method in prompt.'

def print_usage(uage_method1,uage_method2):
    print(uage_method1)
    print(uage_method2)

if len(sys.argv)==2:
    if sys.argv[1]=='-h':
        print_usage(uage_method1,uage_method2)
    sys.exit()
elif len(sys.argv)>=2:
    sp_lc_select  = sys.argv[1]
    evtfilename   = sys.argv[2]
    ehkname       = sys.argv[3]
    gtifile       = sys.argv[4]
    dtname        = sys.argv[5]
    sl_name       = sys.argv[6]
    chmin         = int(sys.argv[7])
    chmax         = int(sys.argv[8])
    outnam        = sys.argv[9]
    if (len(sys.argv)==11):
        slgti     = sys.argv[10]
else:
    sp_lc_select= str(raw_input("Selection(spec/lc):"))
    evtfilename = str(raw_input("Blind detector file:"))
    ehkname     = str(raw_input("EHK file:"))
    gtifile     = str(raw_input("GTI file:"))
    dtname      = str(raw_input("Dead time correction file:"))
    sl_name     = str(raw_input("Source or lightcurve:"))
    chmin      = str(raw_input("Minimum channel:"))
    chmax      = str(raw_input("Maximum channel:"))
    outnam      = str(raw_input("The prefix of output file name:"))
    slgti       = str(raw_input("Specific time range file(NONE):"))




'''Check the time range in GTI'''
def is_ingti(START,STOP,tl,tu):
    num = len(START)
    is_gti = 0
    for ii in xrange(0,num):
        t0=START[ii]
        t1=STOP[ii]
        flag0 = (tl<=t0) & (tu>=t0)
        flag1 = (tl>=t0) & (tu<=t1)
        flag2 = (tl<=t1) & (tu>=t1)
        if flag0 | flag1 | flag2:
            is_gti = 1
            return is_gti
    return is_gti
'''Check the time in GTI '''
def is_ingti2(START,STOP,ti):
    num = np.size(START)
    is_gti = 0
    if num == 1:
        t0=START
        t1=STOP
        flag0 = (ti>=t0) & (ti<=t1)
        if flag0:
            is_gti = 1
            return is_gti
    if num >= 2:
        for ii in xrange(0,num):
            t0=START[ii]
            t1=STOP[ii]
            flag0 = (ti>=t0) & (ti<=t1)
            if flag0:
                is_gti = 1
                return is_gti
    return is_gti
'''Give the tag for specific time'''
def time_gtiflag(time,START,STOP,tflag):
    for ii in xrange(0,len(time)):
        tflag[ii] = is_ingti2(START,STOP,time[ii])

'''Give the index for specific time'''
def flag_selection(tflag,tindex):
    cnt = 0
    for ii in xrange(0,len(tflag)):
        if (tflag[ii] == 1):
            tindex[cnt] = ii
            cnt = cnt+1
    return cnt

'''Give the index for bkg map'''
def bkgmap_index(LON,LAT,ascend_flag ,step):
    lon_index = int(LON/step)
    lat_index = int((LAT+45)/step)
    map_index = lon_index+lat_index*72+ascend_flag*1296
    return map_index

'''Give the index for bkg map for an array'''
def bkgmap_time(lon_arr,lat_arr,ascend_flag,bkgmap_flag):
    fnum = np.size(lon_arr)
    for ii in xrange(0,fnum):
        bkgmap_flag[ii] = bkgmap_index(lon_arr[ii],lat_arr[ii],ascend_flag[ii],5.)

'''Give the data points for specific 5x5 size'''
def bkgmap_num(bkgmap_flag):
    dval = bkgmap_flag[1:(len(bkgmap_flag))] - bkgmap_flag[0:(len(bkgmap_flag)-1)]
    fnum = np.size((np.where(np.abs(dval) > 0))) + 1
    print("5x5 interval number:",fnum)
    return fnum

'''Give the start and stop indices for specific 5x5 size'''
def bkgmap_interval_index(bkgmap_flag,bkgmap_start_index,bkgmap_stop_index):
    fnum = np.size(bkgmap_flag)
    inum = np.size(bkgmap_start_index)
    dval = bkgmap_flag[1:fnum] - bkgmap_flag[0:(fnum-1)]
    nonzero_in = np.where(np.abs(dval) > 0)
    nonzero_num = np.size(nonzero_in)
    print 'Non zeors index',nonzero_in[0:(fnum)]
    bkgmap_start_index[1:(inum)] = nonzero_in + np.ones(nonzero_num,dtype=np.int)
    bkgmap_start_index[0] = 0
    #print np.size(bkgmap_stop_index[0:(inum-2)]),np.size(nonzero_in)
    bkgmap_stop_index[0:(inum-1)] =nonzero_in + np.zeros(nonzero_num,dtype=np.int)
    bkgmap_stop_index[inum-1] = fnum-1

def write_bkgspec(fname,channel,counts,expo,hdr_ext):
    spec_qua= np.zeros(256)
    spec_grp= np.ones(256)
    spec_col1 = pf.Column(name='CHANNEL', format='J', array=channel)
    spec_col2 = pf.Column(name='COUNTS', format='J', array=counts)
    spec_col3 = pf.Column(name='QUALITY', format='I', array=spec_qua)
    spec_col4 = pf.Column(name='GROUPING', format='I', array=spec_grp)
    cols = pf.ColDefs([spec_col1, spec_col2, spec_col3, spec_col4])
    hdr = pf.Header()
    hdr['EXTNAME']  = "SPECTRUM"
    hdr['PHAVERSN'] = "1992a"
    hdr['HDUCLASS'] = "OGIP"
    hdr['HDUCLAS1'] = "SPECTRUM"
    hdr['HDUCLAS2'] = "TOTAL"
    hdr['HDUCLAS3'] = "COUNT"
    hdr['HDUCLAS4'] = "TYPE:I"
    hdr['HDUVERS1'] = "1.2.1"
    hdr['CHANTYPE'] = "PI"
    hdr['DETCHANS'] = hdr_ext['DETCHANS']
    hdr['TELESCOP'] = 'HXMT'
    hdr['INSTRUME'] = 'HE'

    hdr["OBS_MODE"] = hdr_ext['OBS_MODE']
    hdr["DATE-OBS"] = hdr_ext['DATE-OBS']
    hdr["DATE-END"] = hdr_ext['DATE-END']
    hdr["OBJECT"]   = hdr_ext['OBJECT']
    hdr["TSTART"]   = hdr_ext['TSTART']
    hdr["TSTOP"]    = hdr_ext['TSTOP']
    hdr["RA_OBJ"]   = hdr_ext['RA_OBJ']
    hdr["DEC_OBJ"]  = hdr_ext['DEC_OBJ']

    hdr['CORRFILE'] = 'None'
    hdr['CORRSCAL'] = 1.0

    hdr['BACKFILE'] = 'NONE'
    hdr['BACKSCAL'] = 1.0

    hdr['RESPFILE'] = 'NONE'
    hdr['ANCRFILE'] = 'NONE'
    hdr['FILTER']   = 'NONE'

    hdr['AREASCAL'] = 1.0
    hdr['EXPOSURE'] = expo
    hdr['LIVETIME'] = expo
    hdr['DEADC']    = 1.0
    hdr['STATERR']  = True
    hdr['SYSERR']   = False
    hdr['POISSERR'] = True
    hdr['GROUPING'] = 0
    hdr['QUALITY']  = 0
    hdr['MJDREFI']  = hdr_ext['MJDREFI']
    hdr['MJDREFF']  = hdr_ext['MJDREFF']
    hdu = pf.BinTableHDU.from_columns(cols,header=hdr)
    hdu.writeto(fname,overwrite=True)

def write_lcurve(fname,time,counts,hdr_ext):
    lc_frac= np.ones(np.size(time))
    lc_col1 = pf.Column(name='Time', format='D', array=time)
    lc_col2 = pf.Column(name='Counts', format='J', array=counts)
    lc_col3 = pf.Column(name='FRACEXP', format='D', array=lc_frac)
    cols = pf.ColDefs([lc_col1, lc_col2, lc_col3])
    hdr = pf.Header()
    hdr['EXTNAME']  = "RATE"
    hdr['PHAVERSN'] = "1992a"
    hdr['HDUCLASS'] = "OGIP"
    hdr['HDUCLAS1'] = "LIGHTCURVE"
    hdr['HDUCLAS2'] = "ALL"
    hdr['HDUCLAS3'] = "COUNT"
    hdr['HDUCLAS4'] = "TYPE:I"
    hdr['HDUVERS1'] = "1.1.0"
    hdr['CHANTYPE'] = "PI"
    hdr['TELESCOP'] = hdr_ext['TELESCOP']
    hdr['INSTRUME'] = hdr_ext['INSTRUME']
    hdr['TIMEUNIT'] = hdr_ext['TIMEUNIT']
    hdr['MJDREFI']  = hdr_ext['MJDREFI']
    hdr['MJDREFF']  = hdr_ext['MJDREFF']
    hdr["OBS_MODE"] = hdr_ext['OBS_MODE']
    hdr["DATE-OBS"] = hdr_ext['DATE-OBS']
    hdr["DATE-END"] = hdr_ext['DATE-END']
    hdr["OBJECT"]   = hdr_ext['OBJECT']
    hdr["TSTART"]   = hdr_ext['TSTART']
    hdr["TSTOP"]    = hdr_ext['TSTOP']
    hdr["RA_OBJ"]   = hdr_ext['RA_OBJ']
    hdr["DEC_OBJ"]  = hdr_ext['DEC_OBJ']
    hdr['TIMEZERO']  = hdr_ext['TIMEZERO']
    hdr['TIMEDEL']  = hdr_ext['TIMEDEL']

    hdu = pf.BinTableHDU.from_columns(cols,header=hdr)
    hdu.writeto(fname,overwrite=True)


'''Read gti extesion'''

#gtifile = '/hxmt/work/USERS/gemy/work/Crab/P0101299/P010129900101/HXMT_P010129900101_HE-Evt_FFFFFF_V1_L1P_gti.FITS'

hdulist = pf.open(gtifile)
tb = hdulist[1].data
START = tb.field(0)
STOP = tb.field(1)
hdulist.close()
print("GTI START=",START)
print("GTI STOP=",STOP)


'''Read EHK file and position devision by 5 x 5'''

#ehkname = '/hxmt/work/HXMT-DATA/1L/A01/P0101299/P0101299001/P010129900101-20170827-01-01/AUX/HXMT_P010129900101_EHK_FFFFFF_V1_L1P.FITS'
ehklist = pf.open(ehkname)
ehk_tab = ehklist[1].data
ehk_time= ehk_tab.field(0)
ehk_LON = ehk_tab.field(8)
ehk_LAT = ehk_tab.field(9)
ehklist.close()

ehk_num = np.size(ehk_time)
#Ascend: 0
#Descend: 1
ehk_diff = ehk_LAT[1:(ehk_num)] - ehk_LAT[0:(ehk_num-1)] 
ehk_ascend_flag = np.zeros(ehk_num);
ehk_ascend_flag[np.where(ehk_diff >= 0)] = 0
ehk_ascend_flag[np.where(ehk_diff < 0)]  = 1
ehk_ascend_flag[ehk_num-1]  = ehk_ascend_flag[ehk_num-2]

tflag = np.zeros(ehk_num,dtype='int')
tindex = np.zeros(ehk_num,dtype='int')
time_gtiflag(ehk_time,START,STOP,tflag)
ehk_num = flag_selection(tflag,tindex)
ehk_time = ehk_time[tindex[0:(ehk_num)]]
ehk_LON = ehk_LON[tindex[0:(ehk_num)]]
ehk_LAT = ehk_LAT[tindex[0:(ehk_num)]]
ehk_ascend_flag= ehk_ascend_flag[tindex[0:(ehk_num)]]

bkgmap_flag = np.zeros(ehk_num,dtype='int')
bkgmap_time(ehk_LON,ehk_LAT,ehk_ascend_flag,bkgmap_flag)
bkgmap_flag = np.array(bkgmap_flag)
bkgmap_num = bkgmap_num(bkgmap_flag)

bkgmap_start_index = np.zeros(bkgmap_num,dtype='int')
bkgmap_stop_index = np.zeros(bkgmap_num,dtype='int')
bkgmap_interval_index(bkgmap_flag,bkgmap_start_index,bkgmap_stop_index)
bkgmap_arr_num  = bkgmap_stop_index - bkgmap_start_index + 1
bkgmap_arr_expo = bkgmap_stop_index - bkgmap_start_index + 1

bkgmap_start_time = ehk_time[bkgmap_start_index]
bkgmap_stop_time  = ehk_time[bkgmap_stop_index]
bkgmap_flag_uniq  = bkgmap_flag[bkgmap_start_index]

bkgspec_bld_bkgmap = np.zeros((bkgmap_num,256),dtype='float')
bkgspec_all_bkgmap = np.zeros((18*bkgmap_num,259),dtype='float')

print(bkgmap_arr_num)
print(bkgmap_start_time-bkgmap_start_time[0])
print(bkgmap_stop_time-bkgmap_start_time[0])

'''Read Dead-Time file'''
dtimelist = pf.open(dtname)
dtime_tab = dtimelist[1].data
dtime_time = dtime_tab.field(0)
dtime_cyc = dtime_tab.field(1)
dtime_num = np.size(dtime_time)
dtime_arr = np.zeros((dtime_num,18))
dt_cyc = np.zeros(dtime_num)

for ii in xrange(0,18):
    if ii<=5:
        dt_cyc = dtime_cyc[0:(dtime_num),0]
    if ii>=6 & ii <=11:
        dt_cyc = dtime_cyc[0:(dtime_num),1]
    if ii>=12:
        dt_cyc = dtime_cyc[0:(dtime_num),2]

    tmpdt = dtime_tab.field(ii+2)/dt_cyc
    dtime_arr[0:(dtime_num),ii] = tmpdt
dtimelist.close()

dtime_num = np.size(dtime_time)
tflag = np.zeros(dtime_num,dtype='int')
tindex = np.zeros(dtime_num,dtype='int')
time_gtiflag(dtime_time,START,STOP,tflag)
dtime_num = flag_selection(tflag,tindex)
dtime_time=dtime_time[tindex[0:(dtime_num)]]
dtime_cyc=dtime_cyc[tindex[0:(dtime_num)],0:3]
dtime_arr=dtime_arr[tindex[0:(dtime_num)],0:18]

bkgmap_dtc = np.zeros((18,bkgmap_num))
bkgmap_dtt = np.zeros((18,bkgmap_num))

print(np.size(dtime_time))
print(dtime_num)

'''Cal the dead time correction for every time interval'''
for ii in xrange(0,18):
    for jj in xrange(0,bkgmap_num):
        t0 = bkgmap_start_time[jj]
        t1 = bkgmap_stop_time[jj]
        tflag2 = np.zeros(dtime_num,dtype='int')
        tindex2 = np.zeros(dtime_num,dtype='int')
        #print(np.size(dtime_time),dtime_num,dtime_time[0]-t0,dtime_time[dtime_num-1]-t1)
        time_gtiflag(dtime_time,t0,t1,tflag2)
        tmpdt_num = flag_selection(tflag2,tindex2)
        tmpdeadtime = dtime_arr[tindex2[0:tmpdt_num],ii]
        bkgmap_dtc[ii,jj] = np.sum(tmpdeadtime)/np.size(tmpdeadtime)
        bkgmap_dtt[ii,jj] = np.sum(tmpdeadtime)

'''Read DETID==17 event data (Blind detecter)'''

evt_list  = pf.open(evtfilename)
evt_tab   = evt_list[1].data
evt_time  = evt_tab.field(0)
evt_detid = evt_tab.field(1)
evt_cha   = evt_tab.field(2)
evt_type  = evt_tab.field(5)
evt_hdr   = evt_list[1].header
evt_list.close()

bld_spec_arr = np.zeros((bkgmap_num,256))
detid17_index = np.where((evt_detid == 16) & (evt_type == 0))
evt_time  = evt_time[detid17_index]
evt_cha   = evt_cha[detid17_index]

'''Read coe correct channel range'''
#cha_data = np.loadtxt('/home/hxmt/gemy/work/HDPC/hxmtbkg/hxmt_bkgest_v2-0.5/BKG/BldSpec/mchran.txt')
cha_data = np.loadtxt('./auxiliary/mchran.txt')

'''Obtain the blind spectra for each 5x5 degrees'''
cha_ran = np.linspace(0,256,257)
channel = np.linspace(0,255,256)
bld_spec_all_expo=0
bld_spec_all_deadt=np.sum(bkgmap_dtt[16,0:bkgmap_num])
bld_spec_all=np.zeros(256)
for jj in xrange(0,bkgmap_num):
    t0 = bkgmap_start_time[jj]
    t1 = bkgmap_stop_time[jj]
    ttindex = np.where((evt_time >= t0) & (evt_time < t1+1))
    tmpcha = evt_cha[ttindex]
    #print 'Exposure: ', t1-t0+1, ' Photon number: ',np.size(tmpcha)
    tmpspec,bins = np.histogram(tmpcha,bins=cha_ran,range=[0,255])
    bld_spec_all_expo=bld_spec_all_expo+t1-t0+1
    bld_spec_all=bld_spec_all+tmpspec
    bkgmap_dtc
    #plt.figure()
    #plt.plot(channel,tmpspec)
    #plt.show()

bld_spec_all_deadc=bld_spec_all_deadt/bld_spec_all_expo

print("Dead time correction coeffient:",bld_spec_all_deadc,bld_spec_all_expo,bld_spec_all_deadt)

'''
tmpspec,bins = np.histogram(evt_cha,bins=cha_ran,range=[0,255])
for ii in xrange(0,256):
    print bins[ii],tmpspec[ii], np.size(np.where(evt_cha == ii))
'''

'''Read background model'''
#srcmapname='/home/hxmt/gemy/work/HDPC/hxmtbkg/Bkg_coe/HEbkgmap/HE_bkgmap.fits'
srcmapname='./auxiliary/HE_bkgmap.fits'
srclist = pf.open(srcmapname)
srcmap_tab = srclist[1].data
srcmap_IN  = srcmap_tab.field(0)
srcmap_LON = srcmap_tab.field(1)
srcmap_LAT = srcmap_tab.field(2)
srcmap_BKG = srcmap_tab.field(3)

#print(srcmap_IN)
#print(srcmap_LON)
#print(srcmap_LAT)

'''Cal the spectra of blind detectors from map'''
for ii in xrange(0,bkgmap_num):
    tmpindex = bkgmap_flag_uniq[ii]
    tmpspec  = srcmap_BKG[tmpindex,0:4608]
    tin1 = 16*256
    tin2 = 17*256
    bkgspec_bld_bkgmap[ii,0:256] = tmpspec[tin1:tin2]

'''Cal the spectra of all detectors from map'''
for detid in xrange(0,18):
    tin1 = detid*256
    tin2 = (detid+1)*256
    for ii in xrange(0,bkgmap_num):
        tmpindex = bkgmap_flag_uniq[ii]
        tmpspec  = srcmap_BKG[tmpindex,0:4608]
        bkgspec_all_bkgmap[detid*bkgmap_num+ii,0] = detid
        bkgspec_all_bkgmap[detid*bkgmap_num+ii,1] = (bkgmap_start_time[ii]+bkgmap_start_time[ii])/2.
        bkgspec_all_bkgmap[detid*bkgmap_num+ii,2] = bkgmap_arr_expo[ii]
        #print("ii===",ii,tmpindex,"tmpspec==",np.sum(tmpspec[0:256]))
        bkgspec_all_bkgmap[detid*bkgmap_num+ii,3:259] = tmpspec[tin1:tin2]*bkgmap_arr_expo[ii]


'''++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'''
'''++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'''
'''+++++++++++++++++++++++++++++++++++++++Calculate spectrum fro BLD'''
'''++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'''
'''++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'''
spec_bldmod=np.zeros(256)
spec_bldmod_expo=0
spec_ch = np.linspace(0,255,256)
tmpexpo_arr = bkgspec_all_bkgmap[16*bkgmap_num:((16+1)*bkgmap_num),2]
tmpspec_arr = bkgspec_all_bkgmap[16*bkgmap_num:((16+1)*bkgmap_num),3:259]
spec_bldmod= np.sum(tmpspec_arr,axis=0)
spec_bldmod_expo=np.sum(tmpexpo_arr)

print(bld_spec_all_expo,spec_bldmod_expo)
print(np.sum(bld_spec_all),np.sum(spec_bldmod))

#plt.figure()
#plt.plot(channel,bld_spec_all/(1-bld_spec_all_deadc))
#plt.plot(channel,bld_spec_all)
#plt.plot(channel,rr)
#plt.show()
#plt.figure()
#plt.plot(channel,spec_bldmod-(bld_spec_all/(1-bld_spec_all_deadc)))
#plt.show()

coe_arr = np.zeros(6)
for ii in xrange(0,6):
    in1 = int(cha_data[16,ii])
    in2 = int(cha_data[16,ii+1])
    coe_arr[ii] = np.mean(spec_bldmod[in1:in2]/(bld_spec_all[in1:in2]/(1-bld_spec_all_deadc)))

print(coe_arr)

'''++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'''
'''++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'''
'''++++++++++++++++++++++++++  Calculate spectrum    +++++++++++++'''
'''++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'''
'''++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'''

if sp_lc_select == 'spec':

    src_name=[]
    print(sl_name)
    sf = open(sl_name)
    for sline in sf:
        print sline
        src_name.append(sline)
    sf.close()
    print(src_name)
    print("Calculate background spectra now.")
    spec_ch = np.linspace(0,255,256)
    for ii in xrange(0,18):
        tmpexpo_arr = bkgspec_all_bkgmap[ii*bkgmap_num:((ii+1)*bkgmap_num),2]
        tmpspec_arr = bkgspec_all_bkgmap[ii*bkgmap_num:((ii+1)*bkgmap_num),3:259]
        spec_cnt= np.sum(tmpspec_arr,axis=0)
        if(ii <= 20):
            plt.figure()
            plt.plot(spec_cnt,'C1')
            plt.plot(spec_bldmod,'C2')
            plt.plot(spec_cnt-spec_bldmod)
            plt.show()
        for jj in xrange(0,6):
            in1 = int(cha_data[ii,jj])
            in2 = int(cha_data[ii,jj+1])
            spec_cnt[in1:in2] = spec_cnt[in1:in2]/coe_arr[jj]
        tmpstr = src_name[ii]
        tmppos = tmpstr.find('\n')
        if (len(tmpstr[0:tmppos]) == 0):
            print("Input file name error:")
            sys.exit()
        print("For detector:", ii, " src file name: ", tmpstr[0:tmppos])
        spec_list    = pf.open(tmpstr[0:tmppos])
        spec_tab     = spec_list[1].data
        spec_channel = spec_tab.field(0)
        spec_counts  = spec_tab.field(1)
        spec_hdr     = spec_list[1].header
        spec_list.close()
        tmpexpo=np.sum(tmpexpo_arr)
        rr = (spec_counts/spec_hdr['exposure'])/(spec_cnt/tmpexpo)
        rr0=np.mean(rr[200:256])
        print(rr0)
        outname = outnam + '_' + str(ii)+'.pha'
        write_bkgspec(outname,spec_ch,spec_cnt*rr0,tmpexpo,spec_hdr)
        #plt.figure()
        #print("Expo=",tmpexpo)
        #plt.plot(rr)
        #plt.show()




'''++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'''
'''++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'''
'''++++++++++++++++++++++++++  Calculate light curve    +++++++++++++'''
'''++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'''
'''++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'''


if sp_lc_select == 'lc':
    print("Calculate background spectra now.")
    src_name=[]
    print(sl_name)
    sf = open(sl_name)
    for sline in sf:
        print sline
        src_name.append(sline)
    sf.close()
    print(src_name)
    tmpstr = src_name[0]
    tmppos = tmpstr.find('\n')
    if (len(tmpstr[0:tmppos]) == 0):
        print("Input file name error:")
        sys.exit()
    print("For HE src file name: ", tmpstr[0:tmppos])
    lc_list    = pf.open(tmpstr[0:tmppos])
    lc_tab     = lc_list[1].data
    lc_time    = lc_tab.field(0)
    lc_counts  = lc_tab.field(1)
    lc_hdr     = lc_list[1].header
    lc_list.close()
    lc_num = np.size(lc_time)
    lc_bkg     = np.zeros(lc_num)
    lc_bkg_all = np.zeros(lc_num)
    if(chmin <0):
        print("Illigal minmum channel, which will be set to 0")
        chmin=0
    if(chmax > 255):
        print("Illigal maximum channel, which will be set to 255")
        chmmax=255
    
    print("The total light curve: ")
    for idid in xrange(0,18):
        if (idid == 16):
            continue
        print("For detector:", idid)
        for ii in xrange(0,lc_num):
            for jj in xrange(0,bkgmap_num):
                bkgindex0 = idid*bkgmap_num + jj
                tt0 = bkgmap_start_time[jj]
                tt1 = bkgmap_stop_time[jj] + 1
                tmpchmin = chmin + 3
                tmpchmax = chmax + 3
                if (lc_time[ii]>=tt0) & (lc_time[ii]< tt1):
                    tmpexpo_arr = bkgspec_all_bkgmap[bkgindex0,2]
                    tmpspec_arr = bkgspec_all_bkgmap[bkgindex0,tmpchmin:tmpchmax]
                    spec_cnt= np.sum(tmpspec_arr)
                    lc_bkg[ii] = lc_bkg[ii] + spec_cnt/np.sum(tmpexpo_arr)
                    #print(lc_time[ii]-lc_time[0],lc_time[ii]-tt0,tt1-lc_time[ii],bkgindex0,lc_bkg[ii])
    outname = outnam + '_all.lc'
    write_lcurve(outname,lc_time,lc_bkg,lc_hdr)
    #plt.figure()
    #plt.plot(lc_time-lc_time[0],lc_bkg)
    #plt.show()
'''
    for idid in xrange(0,1):
        print("For detector:", idid)
        for ii in xrange(0,lc_num):
            for jj in xrange(0,bkgmap_num):
                bkgindex0 = idid*bkgmap_num + jj
                tt0 = bkgmap_start_time[jj]
                tt1 = bkgmap_stop_time[jj] + 1
                tmpchmin = chmin + 3
                tmpchmax = chmax + 3
                if (lc_time[ii]>=tt0) & (lc_time[ii]< tt1):
                    tmpexpo_arr = bkgspec_all_bkgmap[bkgindex0,2]
                    tmpspec_arr = bkgspec_all_bkgmap[bkgindex0,tmpchmin:tmpchmax]
                    spec_cnt= np.sum(tmpspec_arr)
                    lc_bkg[ii] = spec_cnt/np.sum(tmpexpo_arr)
                    print(lc_time[ii]-lc_time[0],lc_time[ii]-tt0,tt1-lc_time[ii],bkgindex0,lc_bkg[ii])
        outname = outnam + '_' + str(idid)+'.lc'
        write_lcurve(outname,lc_time,lc_bkg,lc_hdr)
        plt.figure()
        plt.plot(lc_time-lc_time[0],lc_bkg)
        plt.show()
        print(lc_bkg)
'''

print("Finish.")





