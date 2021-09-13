# -*- coding: utf-8 -*-
"""
Created on Tue May  4 16:17:05 2021

@author: alega
"""


from functions.read_rinex import read_nav
from functions.cart2geod import cart2geod
from functions.geod2cart import geod2cart
import math
import numpy as np
#from tabulate import tabulate

# Poliastro modules
from poliastro.twobody import Orbit
from poliastro.bodies import Earth

# Astropy modules
from astropy import coordinates as coord
from astropy import units as u

# Plotting modules
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from datetime import datetime

class SatelliteInfo():
    """     Satellite orbit parameters    """
    def __init__( self, file_name, svPRN, long_ref, lat_ref, h_ref, check):
        self.file_name = file_name
        self.sv_number = svPRN
        self.long_ref=long_ref
        self.lat_ref=lat_ref
        self.h_ref=h_ref


    # def satOrbit(self):
        # file_name=input("Enter name of Rinex file with extension: ")

        nav_file=open(file_name, 'r')
        nav=read_nav(nav_file)
        #print(nav)

        file = open("Satellites_positions_output.txt", "w")
        file2 = open("Satellites_velocities_output.txt", "w")
        file.close()
        file2.close()

        # Time
        #t=int(input("Insert time: "))
        positions=[]
        velocities=[]
        
        for item in nav:
           
            # Parameters from navigation message
            prn=int(item[0])
            year=int(item[1])
            month=int(item[2])
            day=int(item[3])
            hour=int(item[4])
            minute=int(item[5])
            second=int(item[6])
            #epoch=str([year, month, day, hour, minute, second])
            clockbias=item[7]
            clockdrift=item[8]
            clockdriftrate=item[9]
            iode=item[10]
            crs=item[11]      #sin correction orbit radius   #meters
            delta_n=item[12]   #this is n_a_delta of is800
            M0=item[13]     #mean anomaly at reference time   #semicircles
            cuc=item[14]     #cos correction lat
            e=item[15]     #eccentricity     #no dimension
            cus=item[16]   #sin correction lat         #radians
            sqrtA=item[17]
            toe=item[18]      #ephemeris rt week   #s   
            cic=item[19]    #cos correction inclination
            omega0_cap=item[20]   #longitude of ascending node of orbit plane at weekly epoch   #semicircles
            cis=item[21]    #sin correction inclination   #radians
            i0=item[22]       #inclination angle at reference time     #semicircles
            crc=item[23]      #cos correction orbit radius
            omega=item[24]    #perigee   #semicircles
            omegadot_cap=item[25]    #rate of right ascension
            IDOT=item[26]   #old i_0_dot?
            codesL2=item[27]
            gps_week=item[28]
            L2P_flag=item[29]
            sv_accuracy=item[30]
            sv_health=item[31]
            tgd=item[32]
            iodc=item[33]
            transmission_time=item[34]
            #fit_interval=item[35]
            
            #rounding time to match sp3 
            sec_diff=0
            if second != 0:
                #continue
                sec_diff=60-second
                second=0
                minute=minute+1
                if minute >= 60 :
                    minute=minute-60
                    hour += 1
                if hour >= 24 :
                    hour=hour-24
                    day+= 1
                if month==1 or month==3 or month==5 or month==7 or month==8 or month==10 or month==12:
                    if day > 31:
                        day=1
                        month+= 1
                elif month==4 or month==6 or month==9 or month==11:
                    if day > 30:
                        day=1
                        month+=1
                elif month==2 and year%4==0:
                      if day > 29:
                        day=1
                        month+=1
                elif month==2 and year%4!=0:
                      if day > 28:
                        day=1
                        month+=1                         
                if month > 12:
                    month=1
                    year += 1
                    
            
            t=[]
            #times (toe iniziale e +5s per 25 volte)
            for i in range(1, 26):
                if sec_diff !=0:
                    t.append(toe+sec_diff+300*(i-1))
                else: 
                    t.append(toe+300*(i-1))  
            
            # Fixed values
            pi=math.atan(1)*4
            capital_omega_dot_ref=-2.6*10**(-9)   #rate ascension rate reference   #semicircles/sec
            earth_grav_const=3.986005 * 10**14   #m^3/s^2
            earth_rotation_rate=7.2921151467 * 10**(-5)   #WGS84   #rad/s
            
            for k in range(1, 26):
                #to get 25 values in time, from start and then one every 5 minutes (range of 2 hours)
                min=minute+5*(k-1)
                h=hour
                d=day
                m=month
                yr=year
                if min >= 60 and min <120:
                    min=min-60
                    h=h+1
                if min>=120:
                    min=min-120
                    h=h+2
                if h == 24 :
                    h=h-24
                    d+= 1
                if h >= 25 :
                    h=h-24
                    d+= 1                   
                if m==1 or m==3 or m==5 or m==7 or m==8 or m==10 or m==12:
                    if d > 31:
                        d=1
                        m+= 1
                elif m==4 or m==6 or m==9 or m==11:
                    if d > 30:
                        d=1
                        m+=1
                elif m==2 and yr%4==0:
                      if d > 29:
                        d=1
                        m+=1
                elif m==2 and yr%4!=0:
                      if d > 28:
                        d=1
                        m+=1                         
                if m > 12:
                    m=1
                    yr += 1
                    
                #------User equations for computing satellite position------#
                
                #correcting time
                time_from_eph_rt= t[k-1] - toe    #s
                if time_from_eph_rt > 302400:
                    time_from_eph_rt -= 604800
                elif time_from_eph_rt < -302400:
                    time_from_eph_rt += 604800
            
                A=sqrtA*sqrtA
                n0=math.sqrt(earth_grav_const/A**3)     #mean motion computed   #rad/s
                #n_a_delta=n_delta_0 + 0.5*n_delta_dot_0*time_from_eph_rt    #mean motion difference from computed value
                n=n0 + delta_n   #mean motion corrected       #n_a
                M= M0 + n*time_from_eph_rt    #mean anomaly  #check if mean_anomaly_rt is correct
            
                # Iterations to find true anomaly
                E0=M    #rad
                Ej=E0
                for j in range(1, 4):   # 3 minimum iterations
                    Ej=Ej + (M-Ej+e*math.sin(Ej))/(1-e*math.cos(Ej))
                Ek=Ej    #rad
                ni=2*math.atan(math.sqrt((1+e)/(1-e))*math.tan(Ek/2))      #true anomaly     #check atan2
                    
                phi= ni + omega    #latitude
                phi_correction=cus*math.sin(2*phi) + cuc*math.cos(2*phi)     #latitude correction
                radial_correction=crs*math.sin(2*phi) + crc*math.cos(2*phi)
                inclination_correction=cis*math.sin(2*phi) + cic*math.cos(2*phi)
                u_k = phi + phi_correction       #corrected latitude
                r_k=A*(1 - e*math.cos(Ek)) + radial_correction    #corrected radius
                i_k=i0 + IDOT*time_from_eph_rt + inclination_correction    #corrected inclination
                    
                x_orb_plane=r_k*math.cos(u_k)    #position in orbital plane
                y_orb_plane=r_k*math.sin(u_k)
                    
                capital_omega_k=omega0_cap + (omegadot_cap - earth_rotation_rate)*time_from_eph_rt \
                    - earth_rotation_rate*toe    #corrected longitude of ascending node


                # Position (Earth fixed coordinates)
                x=x_orb_plane*math.cos(capital_omega_k) - y_orb_plane*math.cos(i_k)*math.sin(capital_omega_k)
                y=x_orb_plane*math.sin(capital_omega_k) + y_orb_plane*math.cos(i_k)*math.cos(capital_omega_k)
                z=y_orb_plane*math.sin(i_k)
                
                
                # User equations for computing satellite velocity
                Ek_dot=n/(1-e*math.cos(Ek))    #eccentric anomaly rate
                ni_dot=Ek_dot*math.sqrt(1-e**2)/(1-e*math.cos(Ek))       #true anomaly rate
                i_k_dot=IDOT + 2*ni_dot*(cis*math.cos(2*u_k) - cic*math.sin(2*u_k))  #nota: in is800 used phi  #corrected inclination rate
                u_k_dot=ni_dot + 2*ni_dot*(cus*math.cos(2*u_k) - cuc*math.sin(2*u_k))  #nota: in is800 used phi  #corrected latitude rate #nota: in is800 used phi
                r_k_dot=e*A*Ek_dot*math.sin(Ek) + 2*ni_dot*(crs*math.cos(2*u_k) - crc*math.sin(2*u_k))   #nota: in is800 used phi  #corrected radius rate
                long_ascending_node_rate=omegadot_cap - earth_rotation_rate
                
                inplane_x_vel=r_k_dot*math.cos(u_k) - r_k*u_k_dot*math.sin(u_k)
                inplane_y_vel=r_k_dot*math.sin(u_k) + r_k*u_k_dot*math.cos(u_k)

                # Velocity (Earth fixed)
                x_vel=-x_orb_plane*long_ascending_node_rate*math.sin(capital_omega_k) \
                        + inplane_x_vel*math.cos(capital_omega_k) \
                            - inplane_y_vel*math.sin(capital_omega_k)*math.cos(i_k) \
                                - y_orb_plane*(long_ascending_node_rate*math.cos(capital_omega_k)*math.cos(i_k) \
                                               - i_k_dot*math.sin(capital_omega_k)*math.sin(i_k))
           
                y_vel=x_orb_plane*long_ascending_node_rate*math.cos(capital_omega_k) \
                    + inplane_x_vel*math.sin(capital_omega_k) \
                        + inplane_y_vel*math.cos(capital_omega_k)*math.cos(i_k) \
                            - y_orb_plane*(long_ascending_node_rate*math.sin(capital_omega_k)*math.cos(i_k) \
                                           + i_k_dot*math.cos(capital_omega_k)*math.sin(i_k))
                             
                z_vel=inplane_y_vel*math.sin(i_k) + y_orb_plane*i_k_dot*math.cos(i_k)
                   
                # Print
                prn_str=str(prn)
                prn_str_zero=prn_str.zfill(2)
                sv_prn='G'+prn_str_zero
                
                #write epoch (year month day hour minute second)
                epoch_print=[yr, m, d, h, min, second]
                
                #check redundancy caused by 2 hours span values (if elem is computed again, using epoch closer to nav message provided data)
                if positions:                    
                    for elem in positions:
                        if elem[0]==epoch_print and elem[1]==sv_prn:
                            positions.remove(elem)
                            
                if velocities:                    
                    for elem in velocities:
                        if elem[0]==epoch_print and elem[1]==sv_prn:
                            velocities.remove(elem) 

                #write on array epoch + positions
                current_position=[epoch_print, sv_prn, x, y, z]
                positions.append(current_position)
                current_velocity=[epoch_print, sv_prn, x_vel, y_vel, z_vel]
                velocities.append(current_velocity)
                
                
        positions.sort()
        velocities.sort()
        
        #print su file
        with open("Satellites_positions_output.txt", "a") as file:
            for item in positions:
                if item[0][4]==0 or item[0][4]==15 or item[0][4]==30 or item[0][4]==45:
                    #prints a value every 15 minutes
                    file.write("%s\n" % item)
                
        with open("Satellites_velocities_output.txt", "a") as file2:
            for item in velocities:
                if item[0][4]==0 or item[0][4]==15 or item[0][4]==30 or item[0][4]==45:
                    file2.write("%s\n" % item)
                
                         

        #----Preparing parameters for azimuth/elevation computations----#
        #cartesian coordinates of ref. point
        if check is True:
            lat_ref_rad=float(lat_ref)*pi/180   #radians for calculation
            long_ref_rad=float(long_ref)*pi/180
            h_ref_rad=float(h_ref)*pi/180
            (x_ref, y_ref, z_ref)=geod2cart(float(lat_ref_rad), float(long_ref_rad), float(h_ref_rad))
            R0=np.array([[-math.sin(long_ref_rad),  math.cos(long_ref_rad), 0], 
                         [-math.sin(lat_ref_rad)*math.cos(long_ref_rad),  -math.sin(lat_ref_rad)*math.sin(long_ref_rad),   math.cos(lat_ref_rad)], 
                         [math.cos(lat_ref_rad)*math.cos(long_ref_rad),  math.cos(lat_ref_rad)*math.sin(long_ref_rad),  math.sin(lat_ref_rad)]
                    ])
            self.sv_azimuth=[]
            self.sv_elevation=[]
        #---------------------------------------------------------------#
                

        #----Conversion to geodetic coordinates and angles computations----#
        prn_used='G'+str(self.sv_number)
        self.sv_lat=[]
        self.sv_long=[]
        self.sv_datetimes=[]
        
        for item in positions:
            if item[1]==prn_used:
                year=str(item[0][0])
                month=str(item[0][1])
                day=str(item[0][2])
                hour=str(item[0][3])
                minute=str(item[0][4])
                second=str(item[0][5])
                epoch_str=year+'/'+month+'/'+day+' '+hour+':'+minute+':'+second
                datetime_object=datetime.strptime(epoch_str, '%Y/%m/%d %H:%M:%S')
                self.sv_datetimes.append(datetime_object)
                    
                sv_x=item[2]
                sv_y=item[3]
                sv_z=item[4]

                (lat, long, h)=cart2geod(float(sv_x), float(sv_y), float(sv_z))
            
                long_deg=long*180/pi   #lambda
                lat_deg=lat*180/pi   #phi

                self.sv_lat.append(lat_deg)
                self.sv_long.append(long_deg)
                
                #-------------Angles calculation--------------#
                if check is True:
                #conversion from GC baseline to LC
                    baseline=[sv_x-x_ref, sv_y-y_ref, sv_z-z_ref]
                    lc=np.dot(R0, baseline)  #local cartesian coordinates #matrix product
                    east=lc[0]
                    north=lc[1]
                    up=lc[2]
                
                    #compute azimuth
                    azimuth=math.atan2(east, north)
                    azimuth_deg=azimuth*180/pi
                    self.sv_azimuth.append(azimuth_deg)
                
                    #compute elevation
                    elevation=math.atan2(up, math.sqrt(east**2 + north**2))
                    elevation_deg=elevation*180/pi
                    self.sv_elevation.append(elevation_deg)
                    
        self.first_datetime=self.sv_datetimes[0]    
        self.last_datetime=self.sv_datetimes[-1]
              