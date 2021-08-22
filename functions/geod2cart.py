# -*- coding: utf-8 -*-
"""
Created on Tue May  4 17:09:28 2021

@author: 39351
"""

import math
import rotationParam

def geod2cart(phi, lam, h):
    #Define the East-West curvature radius
    Rn = rotationParam.a / (math.sqrt(1 - rotationParam.eSquared * (pow(math.sin(phi), 2))))
    
    #Easting
    x = (Rn + h) * math.cos(phi) * math.cos(lam)
    
    #Northing
    y = (Rn+ h) * math.cos(phi) * math.sin(lam)
    
    #Height
    z = (Rn * (1 - rotationParam.eSquared) + h) * math.sin(phi)   
    return (x, y, z)