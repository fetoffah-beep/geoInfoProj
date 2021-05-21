# -*- coding: utf-8 -*-
"""
Created on Fri May 14 16:44:26 2021

@author: 39351
"""

import math
import rotationParam as rp
# value of Earth's universal gravitational parameters
miu = 3.986005 * 10**14

# Speed of light
c = 2.99792458 * 10**8

# F is a constant
F = -2 * math.sqrt(miu) / math.pow(c, 2)

# Relativistic effect
delta_tr = F * rp.e * math.sqrt(rp.a) * math.sin(E_k)

# SV PRN code phase offset
delta_sv = a_f0 + a_f1 * (t - t_oc) + a_f2 * math.pow((t - t_oc), 2) + delta_tr

GPStime = t_sv - delta_sv