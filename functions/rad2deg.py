# -*- coding: utf-8 -*-
"""
Created on Tue May  4 19:39:55 2021

@author: 39351
"""

import math

def rad2deg(rad):
    rad=(rad/math.pi) * 180
    
    #Extract the degree part
    d = math.floor(rad)
    rad = rad - d
    
    #Extract the minute part
    m = math.floor(rad*60)
    rad = rad* 60 - m
    
    #Extract the second part
    s = (rad * 60)
    
    return (d, m, s)