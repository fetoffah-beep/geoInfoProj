# -*- coding: utf-8 -*-
"""
Created on Tue May  4 16:23:59 2021

@author: 39351
"""
import math
import functions.rotationParam as rp


def cart2geod(x, y, z):
    #Define the eccentricity wrt semi-minor axis
    e_b = math.sqrt((rp.a**2 - rp.b**2)/(rp.b**2))

    r = math.sqrt(x**2 + y**2)

    psi  = math.atan2(z , (r * math.sqrt(1 - rp.eSquared)))    
    
    #Longitude
    lam = math.atan2(y , x)    
    
    #Latitude
    phi  = math.atan2((z + e_b**2 * rp.b * pow(math.sin(psi), 3)) , (r - rp.eSquared * rp.a * pow(math.cos(psi), 3)))

    Rn = rp.a / (math.sqrt(1 - rp.eSquared * pow(math.sin(phi), 2)))

    #Geodetic height
    h = (r / math.cos(phi)) - Rn

    return (phi, lam, h)