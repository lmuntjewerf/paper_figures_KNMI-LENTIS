## import packages
import xarray as xr
import numpy as np
import os,sys
from datetime import datetime

## calculation settings
EXP = '2K'
TIME = 'day'
VAR = 'pr'

point_lat = 52.1; point_lon = 5.2     # De Bilt

list_parents = np.arange(1,16+1)
list_members = np.arange(0,9+1)

## Data locations
data_directory   = '/net/pc200272/nobackup/users/wiel/LENTIS/'
output_directory = '/nobackup/users/wiel/LENTIS/datapaper/'

## Define functions
#def cdo_get_point(var,time,ensemble,parent,member,lat,lon):
def cdo_get_point(var,time,ensemble,parent,member,lat_index,lon_index):
    """Select a single grid point from all LENTIS data files"""
    if ensemble == 'PD': letter = 'h'
    elif ensemble == '2K': letter = 's'
    file_in = f"{data_directory}{ensemble}/{time}/{var}/{var}_{letter}{parent:02d}{member}.nc"
    file_out = f"{output_directory}tmp/{var}_{time}_{ensemble}_P{parent}M{member}.nc"
    #os.system(f"cdo remapnn,lon={lon}/lat={lat} {file_in} {file_out}")
    os.system(f"cdo selindexbox,{lon_index+1},{lon_index+1},{lat_index+1},{lat_index+1} {file_in} {file_out}")
    return

## Find nearest actual grid point
if EXP == 'PD': letter = 'h'
elif EXP == '2K': letter = 's'
file_in = f"{data_directory}{EXP}/{TIME}/{VAR}/{VAR}_{letter}010.nc"
ds = xr.open_dataset(file_in)
lat_index = np.where(np.abs(ds.lat.values-point_lat)==np.min(np.abs(ds.lat.values-point_lat)))[0][0]
lon_index = np.where(np.abs(ds.lon.values-point_lon)==np.min(np.abs(ds.lon.values-point_lon)))[0][0]
#point_lat = ds.lat.values[lat_index]
#point_lon = ds.lon.values[lon_index]

## Loop over all ensemble members, extract data
for i_p,P in enumerate(list_parents):
    for i_m,M in enumerate(list_members):
        print(f"- Loop: P = {P}, M = {M}")
        # Do CDO magic (outside Python)
        #cdo_get_point(VAR,TIME,EXP,P,M,point_lat,point_lon)
        cdo_get_point(VAR,TIME,EXP,P,M,lat_index,lon_index)
        # Report time
        print("  .done at", datetime.now().strftime("%H:%M:%S"))
        
## Collect all in one file
da_all = np.full((len(list_parents),len(list_members),3653),np.nan)
for i_p,P in enumerate(list_parents):
    for i_m,M in enumerate(list_members):
        print(f"- Loop: P = {P}, M = {M}")
        # Open data
        file_in = f"{output_directory}tmp/{VAR}_{TIME}_{EXP}_P{P}M{M}.nc"
        da_mem = xr.open_dataset(file_in)[VAR]
        # Store in array
        da_all[i_p,i_m,:] = da_mem[:,0,0]
                  
## Create xarray DataArray and DataSet
da_all = xr.DataArray(da_all,coords={'parent':list_parents,'member':list_members,'time':da_mem.time.values},dims=['parent','member','time'],attrs=da_mem.attrs,name=VAR)
ds_single_point = da_all.to_dataset()
ds_single_point.attrs['lon'] = str(da_mem.lon.values[0])
ds_single_point.attrs['lat'] = str(da_mem.lat.values[0])
## Save to file
ds_single_point.to_netcdf(f"{output_directory}/{VAR}_{TIME}_{EXP}_{da_mem.lat.values[0]:.1f}N_{da_mem.lon.values[0]:.1f}E.nc")
## Remove tmp files
os.system(f"rm -f {output_directory}tmp/{VAR}_{TIME}_{EXP}_P*M*.nc")

