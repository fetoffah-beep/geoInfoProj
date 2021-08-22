# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 19:40:04 2020

@author: 39351
"""

import math
import numpy as np

def saastamoinenModel (h, eta):
    if (h > -500) and (h < 5000):
        eta #satellite elevation in radians
        Po = 1013.25 #mBar
        To = 291.15 #degree Kelvin
        Ho = 50/100
        ho = 0
        height = h - ho # h is the ellipsoidal height of the receiver
        Pr = Po * (1-0.0000226 * height)**5.225 #pressure
        Tr = To - 0.0065 * height #temperature
        Hr = Ho * math.exp(-0.0006396 * height)
        er = Hr * math.exp(-37.2465 + (0.213166 * Tr) - 0.000256908 * (Tr)**2) #humidity
        tropoDelay = 0.002277 / math.sin(eta) * (Pr + er * (1255/Tr + 0.05) - (math.tan(eta)) ** -2)
        return tropoDelay
    
    else:
        tropoDelay = 0
        return tropoDelay