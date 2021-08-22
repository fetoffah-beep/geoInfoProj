# -*- coding: utf-8 -*-
"""
Created on Fri May 14 16:43:08 2021

@author: 39351
"""

import math

# Speed of light in meters per second
c = 2.99792458 * 10**8

gamma = math.pow((1575.42 / 1227.6), 2)

#TD is the 

T_GD = (1 / (1 - gamma)) * (t_LiP - t_LiP) # where i is the ith frequency the signal is transmitted from the SV antenna phase center



ISC_L1CA = t_L1P - t_L1CA
ISC_L2C = t_L1P - t_L2C

# PR is pseudorange corrected for ionospheric effects
# PRi is pseudorange measured on the channel indicated by the subscript
# ISCi is inter-signal correction for the channel indicated by the subscript
PR = (PR_L2C - gamma_12 * PR_L1CA + c * (ISC_L2C - gamma_12 * ISC_L1CA)) / (1 - gamma_12) - c * T_GD


