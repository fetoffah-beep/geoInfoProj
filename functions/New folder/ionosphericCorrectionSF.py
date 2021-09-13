# -*- coding: utf-8 -*-
"""
Created on Fri May 14 12:57:05 2021

@author: 39351
"""

# This script contains the ionospheric error correction for a single frequency receiver
# It is estimated that the use of this model will provide at least a 50 percent reduction in
# the single - frequency user's RMS error due to ionospheric propagation effects.

import math


# phi_u = user geodetic latitude (semi-circles) WGS 84
# lambda_u = user geodetic longitude (semi-circles) WGS 84
# A = azimuth angle between the user and satellite
# E  = elevation angle between satellite and receiver
# GPStime = receiver computed system time



def ionoCorrection(phi_u, lambda_u, A, E, GPStime, ionoParams):
    # elevation from 0 to 90 degrees
    E = abs(E);
        
    # conversion to semicircles
    phi_u = phi_u / 180;
    lambda_u = lambda_u / 180;
    A = A / 180;
    E = E / 180;
    # Speed of light
    c = 2.99792458 * 10**8
    # c = math.pow((1575.42/1227.6 ), 2)

    alpha = ionoParams[0:3]
    beta = ionoParams[4:7]
    
    # Psi is the Earth's central angle between the user position and the earth projection of ionospheric intersection point
    psi = 0.0137 / (E + 0.11) - 0.022       
    
    phi_i = phi_u + psi * math.cos(A * math.pi)
    
    if abs(phi_i) <= 0.416:
        phi_i = phi_i
    elif phi_i > 0.416:
        phi_i = 0.416
    elif phi_i < -0.416:
        phi_i = -0.416
    
    
    # geodetic longitude of the earth projection of the ionospheric intersection point
    lambda_i = lambda_u + psi * math.sin(A * math.pi) / math.cos(phi_i * math.pi)
    
    # geomagnetic latitude of the earth projection of the ionospheric intersection point
    phi_m = phi_i + 0.064 * math.cos((lambda_i - 1.617) * math.pi)
    
    # The local time in seconds
    t = 4.32 * 10**4 * lambda_i + GPStime
    
    if t >= 86400:
        t = t - 86400
    elif t < 0:
        t = t + 86400
    
    # Obliquity factor
    F = 1 + 16 * math.pow((0.53 - E), 3)        
    
    PER = 0
    for n in range(3):
        PER = PER + beta[n] * math.pow(phi_m, n)        
        
    if PER < 72000:
        PER = 72000
    
    x = 2 * math.pi * (t - 50400) / PER
    
    
    AMP = 0
    for n in range(3):
        AMP  = AMP + alpha[n] * math.pow(phi_m, n)      # the coefficients of a cubic equation representing the amplitude of the vertical delay (4 coefficients - 8 bits each)
    
    if AMP < 0:
        AMP = 0
    
    if abs(x) >= 1.57:
        T_iono = c *  F * 5 * 10**-9
    else:
        T_iono = c * F * ((5 * 10**-9) + AMP * (1 - (x**2/2) + (x**4 / 24)))
    
    return T_iono