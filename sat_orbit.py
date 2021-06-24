# -*- coding: utf-8 -*-
"""
Created on Tue May  4 16:17:05 2021

@author: alega
"""
import math

# to add
#clock correction
#relativistic effect
#check coordinate conversions
from read_rinex import read_nav

file_name=input("Enter name of Rinex file with extension: ")
nav_file=open(file_name, 'r')
nav=read_nav(nav_file)
#print(nav)

file1 = open("Output.txt", "w")
file1.write("sv_prn, time-toe, x, y, z, xdot, ydot, zdot \n")
file1.close()

# Time
t=int(input("Insert time: "))

for item in nav:
    # Parameters from navigation message
    prn=int(item[0])
    #epoch=item[1]
    year=int(item[1])
    print(year)
    month=int(item[2])
    print(month)
    day=int(item[3])
    hour=int(item[4])
    minute=int(item[5])
    second=int(item[6])
    #epoch=[year, month, day, hour, minute, second]
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
    
    # Fixed values
    pi=3.1415926535898
    #A_ref=26559710   #semimajor axis reference   #meters
    capital_omega_dot_ref=-2.6*10**(-9)   #rate ascension rate reference   #semicircles/sec
    earth_grav_const=3.986005 * 10**14   #m^3/s^2
    earth_rotation_rate=7.2921151467 * 10**(-5)   #WGS84   #rad/s
    
    # User equations for computing satellite position
    time_from_eph_rt= t - toe    #s
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

    capital_omega_k=omega0_cap + (capital_omega_dot_ref - earth_rotation_rate)*time_from_eph_rt \
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
    sv_prn='G'+str(prn)
    print("sv:", sv_prn)
    print("at time:", t)
    print("sv position:")
    print(x)
    print(y)
    print(z)
    print("sv components of velocity:")
    print(x_vel)
    print(y_vel)
    print(z_vel)
    
    #printing on file
    sat_values=[sv_prn, time_from_eph_rt, x, y, z, x_vel, y_vel, z_vel]
    file1 = open("Output.txt", "a")
    file1.writelines("%s\n" % str(sat_values))

file1.close()

print()
input('Press ENTER to close');