# -*- coding: utf-8 -*-
"""
Created on Tue May 25 19:06:25 2021

@author: alega
"""
#for Gps navigation messages
#for Rinex 3.xx

# Reading the Ionospheric Parameters

def getSatellitePRN(file_rinex):

    svsPRN = []
    
    with open(file_rinex,'r') as file:
        for line in file:
            if 'END OF HEADER' in line:
                for line in file:
                    if line.startswith('G'):
                        words = line.split()
                        svsPRN.append(words[0][1:3])
    
    return list(set(svsPRN))
    


def readIonosphericParamters(file_rinex):

    ionosphericParam = []
    
    with open(file_rinex,'r') as file:
        for line in file:
            line=line.replace('D', 'e')
            line=line.replace('E', 'e')
            if line.startswith('GPSA'):
                wordList = []
                for word in line.split():
                    
                    wordList.append(word)
                
                alpha0 = float(wordList[1])
                alpha1 = float(wordList[2])
                alpha2 = float(wordList[3])
                alpha3 = float(wordList[4])
                
            elif line.startswith('GPSB'):
                wordList = []
                for word in line.split():
                    
                    wordList.append(word)
                
                beta0 = float(wordList[1])
                beta1 = float(wordList[2])
                beta2 = float(wordList[3])
                beta3 = float(wordList[4])
                ionosphericParam.append([alpha0, alpha1, alpha2, alpha3, beta0, beta1, beta2, beta3])
        
    return ionosphericParam


# Reading the time correction Parameters
def readTimeCorrParamters(file_rinex):

    timeCorrParam = []
    
    with open(file_rinex,'r') as file:
        for line in file:
            line=line.replace('D', 'e')
            line=line.replace('E', 'e')
            if line.startswith('GPUT'):
                wordList = []
                for word in line.split():
                    
                    wordList.append(word)
                
                # a0, a1 coefficients of linear polynomial
                alpha = wordList[1].split('-')
                alpha0 = float('-' + alpha[1] + '-' + alpha[2])
                alpha1 = float('-' + alpha[3] + '-' + alpha[4])
                
                # Reference time for polynomial
                referenceTime = float(wordList[2])
                
                # Reference week number
                weekNUmber = float(wordList[3])
                
                
                # Append values to the timeCorrParam list
                timeCorrParam.append([alpha0, alpha1, referenceTime, weekNUmber])
                
                print(timeCorrParam)
        
                
    return timeCorrParam


# Reading the contents of navigation message 

def read_nav(file_rinex):

    
    while True:
        if 'END OF HEADER' in file_rinex.readline():
            break;
          
    nav=[]
    while  True:
        line=file_rinex.readline()
        line=line.replace('D', 'e')
        if not line:
            break
        if line[0]=='G':
            x=0
            sat=[]
        #check indexes
        if x==0:
            prn=line[1:3]
            year=line[4:8]
            month=line[9:11]
            day=line[12:14]
            hour=line[15:17]
            minute=line[18:20]
            second=line[21:23]
            clockbias=line[23:42]
            clockdrift=line[42:61]
            clockdriftrate=line[61:80]
            sat.append([prn, year, month, day, hour, minute, second, clockbias, clockdrift, clockdriftrate])
        elif x==1:
            iode=line[4:23]
            crs=line[23:42]
            delta_n=line[42:61]
            M0=line[61:80]
            sat.append([iode, crs, delta_n, M0])
        elif x==2:
            cuc=line[4:23]
            e=line[23:42]       #eccentricity
            cus=line[42:61]
            sqrtA=line[61:80]
            sat.append([cuc, e, cus, sqrtA])
        elif x==3:
            toe=line[4:23]
            cic=line[23:42]
            omega0=line[42:61]
            cis=line[61:80]
            sat.append([toe, cic, omega0, cis])
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
            #fit_interval=line[23:42]
            #sat.append([transimission_time, fit_interval])
            sat.append([transimission_time])
            flat_sat=[item for sublist in sat for item in sublist]
            flat_sat=[float(i) for i in flat_sat]
            nav.append(flat_sat)
        
        x += 1      
        
    file_rinex.close()
    return nav


