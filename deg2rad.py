# -*- coding: utf-8 -*-
"""
Created on Tue May  4 19:38:40 2021

@author: 39351
"""

import math

def deg2rad(d, m, s):
    sec= s
    #Convert seconds to minutes adn add to the minute part
    minu= (m+sec)/60
    
    #Convert the minute and the given degree
    deg= (minu+d)/60
    
    #Compute the radian
    rad = (deg/180) * math.pi
    return rad