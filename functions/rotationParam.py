# -*- coding: utf-8 -*-
"""
Created on Tue May  4 19:47:06 2021

@author: 39351
"""

import math

#Semi-major axis
a=6378137

#Flattening
f = 1 / 298.257222100882711243

#Semi-minor axis
b = a - (f * a)

#Eccentricity
e = math.sqrt(1 - b**2 / a**2)

# Square of eccentricity
eSquared = f * (2-f)