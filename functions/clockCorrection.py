# -*- coding: utf-8 -*-
"""
Created on Wed May  5 00:00:15 2021

@author: 39351
"""

import math


def clockCorrection():
	delta_t_SV = af0 + delta_af0 + (af1 + delta_af1) * (t - t_OC) + af2 * pow((t - t_OC), 2) + delta_tr
	return delta_t_SV