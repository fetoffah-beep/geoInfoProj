# -*- coding: utf-8 -*-
"""
Created on Fri Jun  4 14:55:54 2021

@author: 39351
"""

def geometricRange(receiverPos_ECI, gps_SV_POS_ECI, tR, t_T):
    n = receiverPos_ECI * tR - gps_SV_POS_ECI * t_T
    range = abs(n)
    return range