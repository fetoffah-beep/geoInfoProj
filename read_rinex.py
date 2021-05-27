# -*- coding: utf-8 -*-
"""
Created on Tue May 25 19:06:25 2021

@author: alega
"""
#for Gps navigation messages
#for Rinex 3.xx

def read_nav(file_rinex):
    
    while True:
        if 'END OF HEADER' in file_rinex.readline():
            break;
          
    nav=[]
    while  True:
        line=file_rinex.readline()
        if not line:
            break
        if line[0]=='G':
            x=0
            sat=[]
            epoch=[]
        #check indexes
        if x==0:
            prn=line[1:3]
            year=line[4:8]
            month=line[9:11]
            day=line[12:14]
            hour=line[15:17]
            minute=line[18:20]
            second=line[21:23]
            epoch.append([year,
                         month,
                         day,
                         hour,
                         minute,
                         second])
            clockbias=line[23:42]
            clockdrift=line[42:61]
            clockdriftrate=line[61:80]
            flat_epoch=[item for sublist in epoch for item in sublist]
            sat.append([prn, flat_epoch, clockbias, clockdrift, clockdriftrate])
        elif x==1:
            iode=line[4:23]
            crs=line[23:42]
            delta_n=line[42:61]
            M0=line[61:80]
            sat.append([iode, crs, delta_n, M0])
        elif x==2:
            cuc=line[4:23]
            e=line[23:42]
            cus=line[42:61]
            sqrtA=line[61:80]
            sat.append([cuc, e, cus, sqrtA])
        elif x==3:
            toe=line[4:23]
            cic=line[23:42]
            omega=line[42:61]
            cis=line[61:80]
            sat.append([toe, cic, omega, cis])
        elif x==4:
            i0=line[4:23]
            crc=line[23:42]
            omega=line[42:61]
            omegadot=line[61:80]
            sat.append([i0, crc, omega, omegadot])
        elif x==5:
            IDOT=line[4:23]
            codesL2=line[23:42]
            gps_week=line[42:61]
            L2P_flag=line[61:80]
            sat.append([IDOT, codesL2, gps_week, L2P_flag])
        elif x==6:
            sv_accuracy=line[4:23]
            sv_health=line[23:42]
            tgd=line[42:61]
            iodc=line[61:80]
            sat.append([sv_accuracy, sv_health, tgd, iodc])
        elif x==7:    
            transimission_time=line[4:23]
            fit_interval=line[23:42]
            sat.append([transimission_time, fit_interval])
            flat_sat=[item for sublist in sat for item in sublist]
            nav.append(flat_sat)
            print(nav)
        
        x += 1      
        
    file_rinex.close()
    return nav