## import packages
import xarray as xr
import numpy as np
import sys
from datetime import datetime

## calculation settings
EXP = '2K'
TIME = 'day'
VAR = 'tas'

list_parents = np.arange(1,16+1)
list_members = np.arange(0,9+1)
if len(sys.argv) > 1:
    list_parents = [int(sys.argv[1])]
    try: 
        list_members = [int(sys.argv[2])]
    except:
        None
    one_by_one = True
else:
    one_by_one = False
point_lat = 52.1; point_lon = 5.2     # De Bilt

## Data locations
data_directory   = '/net/pc200272/nobackup/users/wiel/LENTIS/'
output_directory = '/nobackup/users/wiel/LENTIS/datapaper/'

## define functions
def open_data_LENTIS_ensmem(var,time,ensemble,parent,member,preproc):
    """Open LENTIS single ensemble member data """
    if ensemble == 'PD': letter = 'h'
    elif ensemble == '2K': letter = 's'
    files = f"{data_directory}{ensemble}/{time}/{var}/{var}_{letter}{parent:02d}{member}.nc"
    ds = xr.open_mfdataset(files,preprocess=preproc,chunks=-1,parallel=True)
    return ds
def pp_sel_point(ds):
    """ Preprocess: select single grid point """
    return ds.sel(lat=point_lat,lon=point_lon, method="nearest")

# Preparation
da_all = np.full((len(list_parents),len(list_members),3653),np.nan)

# Loop over all ensemble members
for i_p,P in enumerate(list_parents):       # 16 parents - or what is given in the arguments
    for i_m,M in enumerate(list_members):   # 10 members - or what is given in the arguments
        print(f"- Loop: P = {P}, M = {M}")
        # Open LENTIS data
        da_ensmem = open_data_LENTIS_ensmem(VAR,TIME,EXP,P,M,pp_sel_point)[VAR].load()
        # Store in one data array
        da_all[i_p,i_m,:] = da_ensmem
        # Empty memory
        if not (P == list_parents[-1] and M == list_members[-1]):
            del da_ensmem
        # Report time
        print("  .done at", datetime.now().strftime("%H:%M:%S"))
        
# Create xarray DataArray and DataSet
print(f"- Create proper xarray")
da_all = xr.DataArray(da_all,coords={'parent':list_parents,'member':list_members,'time':da_ensmem.time.values},dims=['parent','member','time'],attrs=da_ensmem.attrs,name=VAR)
ds_single_point = da_all.to_dataset()

# Save to file
print(f"- Save to file")
if not one_by_one:
    ds_single_point.to_netcdf(f"{output_directory}/{VAR}_{TIME}_{EXP}_{da_ensmem.lat.values:.1f}N_{da_ensmem.lon.values:.1f}E.nc")
else:
    if len(list_members) == 1:
        ds_single_point.to_netcdf(f"{output_directory}/{VAR}_{TIME}_{EXP}_{da_ensmem.lat.values:.1f}N_{da_ensmem.lon.values:.1f}E_P{list_parents[0]}M{list_members[0]}.nc")
    else:
        ds_single_point.to_netcdf(f"{output_directory}/{VAR}_{TIME}_{EXP}_{da_ensmem.lat.values:.1f}N_{da_ensmem.lon.values:.1f}E_P{list_parents[0]}.nc")

