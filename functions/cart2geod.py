# -*- coding: utf-8 -*-
"""
Created on Tue May  4 16:23:59 2021

@author: 39351
"""
import math
import rotationParam


def cart2geod(x, y, z):
    #Define the eccentricity wrt semi-minor axis
    e_b = math.sqrt((rotationParam.a**2 - rotationParam.b**2)/(rotationParam.b**2))

    r = math.sqrt(x**2 + y**2)

    psi  = math.atan(z / (r * math.sqrt(1 - rotationParam.eSquared)))    
    
    #Longitude
    lam = math.atan(y / x)    
    
    #Latitude
    phi  = math.atan((z + e_b**2 * rotationParam.b * pow(math.sin(psi), 3)) / (r - rotationParam.eSquared * rotationParam.a * pow(math.cos(psi), 3)))

    Rn = rotationParam.a / (math.sqrt(1 - rotationParam.eSquared * pow(math.sin(phi), 2)))

    #Geodetic height
    h = (r / math.cos(phi)) - Rn

    return (phi, lam, h)