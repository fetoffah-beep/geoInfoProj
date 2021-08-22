# -*- coding: utf-8 -*-
"""
Created on Fri Jun  4 13:31:05 2021

@author: 39351
"""
import math


rotationRate = 7.2921151467 * 10**-5                    #rad/sec WGS 84 value of the earth's rotation rate

anlge = rotationRate (t-t_0)        #t_0 is the ECEF and ECI coincidence time

def ecef2eci(x_ECEF, y_ECEF, z_ECEF):
    x_ECI = x_ECEF * math.cos(angle) - y_ECEF * math.sin(angle)
    y_ECI = x_ECEF * math.sin(angle) + y_ECEF * math.cos(angle)
    z_ECI = z_ECEF
    return (x_ECI, y_ECI, z_ECI)