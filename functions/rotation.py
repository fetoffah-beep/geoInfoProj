# -*- coding: utf-8 -*-
"""
Created on Wed May  5 00:00:15 2021

@author: 39351
"""

import math
import numpy as np


def rotation(r1, r2, r3):
    # Rotation about the X-axis
    Rx = np.array([[1,  0,              0], 
                   [0,  math.cos(r1),   math.sin(r1)], 
                   [0,  -math.sin(r1),  math.cos(r1)]
               ])
    
    # Rotation about the Y-axis
    Ry = np.array([[math.cos(r2),   0,  -math.sin(r2)], 
                   [0,              1,  0], 
                   [math.sin(r2),   0,  math.cos(r2)]
               ])
    
    # Rotation about the Z-axis
    Rz = np.array([[math.cos(r3),   math.sin(r3),   0], 
                   [-math.sin(r3),  math.cos(r3),   0], 
                   [0,              0,              1]
               ])
    
    # Final rotation matrix
    rotation = Rz * Ry * Rx
    
    return rotation