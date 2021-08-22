import pandas as pd
import georinex as gr
import read_rinex
import xarray
# meas selects a particular channel to read
dat = gr.load('log0052q.18O', meas=['C1', 'L1'])

# Read th header file
hdr = gr.rinexheader('log0052q.18O')

# Select a particular satellite vehicle
hdr = dat.sel(sv='G12').dropna(dim='time',how='all')
#print(hdr)
Eind = dat.sv.to_index().str.startswith('G')
Edata = dat.isel(sv=Eind)
obs = xarray.open_dataset(dat)
print(obs)