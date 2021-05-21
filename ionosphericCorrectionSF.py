# -*- coding: utf-8 -*-
"""
Created on Fri May 14 12:57:05 2021

@author: 39351
"""

# This script contains the ionospheric error correction for a single frequency receiver
# It is estimated that the use of this model will provide at least a 50 percent reduction in
# the single - frequency user's RMS error due to ionospheric propagation effects.

import math
from GPStime import GPStime

# Psi is the Earth's central angle between the user position and the earth projection of ionospheric intersection point
psi = 0.0137 / (E + 0.11) - 0.022       # E is the elevation angle between the satellite and the user 


# geodetic latitude of the earth projection of the ionospheric intersection point where
# A is the azimuth angle between the user and satellite, measured clockwise positive from the true North 
phi_i = phi_u + psi * math.cos(A)

if abs(phi_i) <= 0.416:
    phi_i = phi_i
elif phi_i > 0.416:
    phi_i = 0.416
elif phi_i < -0.416:
    phi_i = -0.416


# geodetic longitude of the earth projection of the ionospheric intersection point
lambda_i = lambda_u + psi * math.sin(A) / math.cos(phi_i)

# geomagnetic latitude of the earth projection of the ionospheric intersection point
phi_m = phi_i + 0.064 * math.cos(lambda_i - 1.617)

# The local time in seconds
t = 4.32 * 10**4 * lambda_i + GPStime

if t >= 86400:
    t = t - 86400
elif t < 0:
    t = t + 86400


F = 1 + 16 * math.pow((0.53 - E), 3)        # Obliquity factor

PER = 0
for n in range(4):
    PER = PER + beta[n] * math.pow(phi_m, n)        # beta is the the coefficients of a cubic equation representing the period of the model (4 coefficients - 8 bits each)

if PER < 72000:
    PER = 72000


x = 2 * math.pi * (t - 50400) / PER


AMP = 0
for n in range(4):
    AMP  = AMP + alpha[n] * math.pow(phi_m, n)      # the coefficients of a cubic equation representing the amplitude of the vertical delay (4 coefficients - 8 bits each)

if AMP < 0:
    AMP = 0
    

def ionoCorrection(x, AMP, F):
    if abs(x) >= 1.57:
        T_iono = F * 5 * 10**-9
    else:
        T_iono = F * ((5 * 10**-9) + AMP * (1 - (x**2/2) + (x**4 / 24)))
    return T_iono