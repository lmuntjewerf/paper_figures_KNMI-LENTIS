## import packages
import xarray as xr
import numpy as np
import os,sys
from datetime import datetime

## calculation settings
EXP = '2K'
TIME = 'Omon'
VAR = 'tos'

point_lat_1 = -5; point_lat_2 = 5; point_lon_1 = -170; point_lon_2 = -120; box_name = 'nino34'     # Nino3.4

list_parents = np.arange(1,16+1)
list_members = np.arange(0,9+1)

## Data locations
data_directory   = '/net/pc200272/nobackup_1/users/wiel/LENTIS/'
output_directory = '/nobackup/users/wiel/LENTIS/datapaper/'

## Define functions
def cdo_box_mean(var,time,ensemble,parent,member,lat_1,lat_2,lon_1,lon_2,name):
    """Select a box of points from all LENTIS data files"""
    if ensemble == 'PD': letter = 'h'
    elif ensemble == '2K': letter = 's'
    file_in = f"{data_directory}{ensemble}/{time}/{var}/{var}_{letter}{parent:02d}{member}.nc"
    file_out_1 = f"{output_directory}tmp/{var}_{time}_{ensemble}_P{parent}M{member}_region.nc"
    os.system(f"cdo sellonlatbox,{lon_1},{lon_2},{lat_1},{lat_2} {file_in} {file_out_1}")
    file_out_2 = f"{output_directory}tmp/{var}_{time}_{ensemble}_P{parent}M{member}_{name}.nc"
    os.system(f"cdo fldmean {file_out_1} {file_out_2}")
    return

## Loop over all ensemble members, extract data
for i_p,P in enumerate(list_parents):
    for i_m,M in enumerate(list_members):
        print(f"- Loop: P = {P}, M = {M}")
        # Do CDO magic (outside Python)
        cdo_box_mean(VAR,TIME,EXP,P,M,point_lat_1,point_lat_2,point_lon_1,point_lon_2,box_name)
        # Report time
        print("  .done at", datetime.now().strftime("%H:%M:%S"))
        
## Collect all in one file
if TIME == 'day':        da_all = np.full((len(list_parents),len(list_members),3653),np.nan)
elif TIME[1:] == 'mon':  da_all = np.full((len(list_parents),len(list_members),120),np.nan)
for i_p,P in enumerate(list_parents):
    for i_m,M in enumerate(list_members):
        print(f"- Loop: P = {P}, M = {M}")
        # Open data
        file_in = f"{output_directory}tmp/{VAR}_{TIME}_{EXP}_P{P}M{M}_{box_name}.nc"
        da_mem = xr.open_dataset(file_in)[VAR]
        # Store in array
        da_all[i_p,i_m,:] = da_mem[:,0,0]
                  
## Create xarray DataArray and DataSet
da_all = xr.DataArray(da_all,coords={'parent':list_parents,'member':list_members,'time':da_mem.time.values},dims=['parent','member','time'],attrs=da_mem.attrs,name=VAR)
ds_single_point = da_all.to_dataset()
ds_single_point.attrs['box'] = f"{point_lat_1} to {point_lat_2}N, {point_lon_1} to {point_lon_2}E"
## Save to file
ds_single_point.to_netcdf(f"{output_directory}/{VAR}_{TIME}_{EXP}_{box_name}.nc")
## Remove tmp files
os.system(f"rm -f {output_directory}tmp/{VAR}_{TIME}_{EXP}_P*M*.nc")

