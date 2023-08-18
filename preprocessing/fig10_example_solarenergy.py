
## import packages
import xarray as xr
import numpy as np
import sys
import warnings
warnings.filterwarnings("ignore")     # ignore warnings in pp_sel_point (.get_loc)
from datetime import datetime

## calculation settings
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
EXP = 'PD'
point_lat = 52.1; point_lon = 5.2     # De Bilt

## data locations
data_directory='/net/pc200272/nobackup/users/wiel/LENTIS/'
output_directory='/nobackup/users/wiel/LENTIS/datapaper/'

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

## Solar energy model
cT_c1 = 4.3     # constant [dC]
cT_c2 = 0.943   # constant [-]
cT_c3 = 0.028   # constant [dC m2 W-1]
cT_c4 = -1.528  # constant [dC s m-1]
gamma = -0.005  # constant [--]
t_ref = 25      # reference temperature [dC]
pi = np.pi
kelvin = 273.15 # Kelvin to degrees Celsius
Gstc = 1000     # standard test conditions [W m-2]
shift_doy = 186 # if 360-day calendar : 180
def day_length(da):
    """ Aim: Computes the number of daylight hours at locations and times for a given dataset """
    day_of_year = da.time.dt.dayofyear
    lat = da.lat
    p = 0. 
    P = np.arcsin(0.39795 * np.cos(0.2163108 + 2 * np.arctan(0.9671396 * np.tan(0.00860*(day_of_year-shift_doy)))))
    arg = ((np.sin(p*pi/180) + np.sin(lat*pi/180) * np.sin(P)) / (np.cos(lat*pi/180) * np.cos(P)))
    arg = xr.where(arg < -1, -1, arg)
    arg = xr.where(arg > 1, 1, arg)
    da_daylight_hours = 24 - 24/pi * np.arccos(arg)
    return da_daylight_hours
def solar_cell_temp(da_rsds, da_tas, da_tasmax, da_wind):
    """ Aim: Computes solar cell temperature """
    da_tasday = (da_tas + da_tasmax)/2
    da_cell_temp = cT_c1 + cT_c2*da_tasday + cT_c3**da_rsds + cT_c4*da_wind
    return da_cell_temp
def solar_perf_ratio(da_cell_temp):
    """ Aim: Computes performance ratio of the solar cell """
    da_pr = 1 + gamma*(da_cell_temp-t_ref)
    return da_pr
def solar_potential(da_pr,da_rsds):
    """
    Aim: Computes theoretical solar power potential 
    """
    da_pot = da_pr * da_rsds / Gstc    
    return da_pot
def compute_solar_energy_production(da_rsds,da_tas,da_tasmax,da_wind):
    """ Aim: Main solar energy computation function, here stopped at the computation of potentials [fraction] rather than actual production [TWh/day]. """
    # compute daylight hours [h/d]
    da_daylight_hours = day_length(da_tas)
    # correct radiation for daylight hours [W m-2]
    da_rsds_day = da_rsds * 24 / da_daylight_hours
    da_rsds_day = xr.where(da_daylight_hours==0, 0, da_rsds_day)
    # unit conversion [degC]
    da_tas = da_tas - kelvin
    da_tasmax = da_tasmax - kelvin
    # compute cell temperature
    da_cell_temp = solar_cell_temp(da_rsds_day, da_tas, da_tasmax, da_wind)
    # compute performance ratio
    da_PR = solar_perf_ratio(da_cell_temp)
    # compute potential [0-1]
    da_solar_pot = solar_potential(da_PR, da_rsds_day)
    da_solar_pot.name = 'PVpot'
    da_solar_pot.attrs = da_rsds.attrs
    da_solar_pot.attrs['units'] = ''
    """# compute capacity factors [0-1 h]
    da_solar_cf = da_solar_pot * da_daylight_hours
    # compute production
    da_solar_prod = (da_solar_cf * da_solar_distr) /10**6
    da_solar_prod.id = 'solar'
    da_solar_prod.units = 'TWh d**-1'
    da_solar_prod.long_name = 'Solar energy production'"""
    # done
    return da_solar_pot

## GOGOGOGO do computation

# Preparation
da_tas = np.full((len(list_parents),len(list_members),3653),np.nan)
da_tasmax = np.full((len(list_parents),len(list_members),3653),np.nan)
da_rsds = np.full((len(list_parents),len(list_members),3653),np.nan)
da_wind = np.full((len(list_parents),len(list_members),3653),np.nan)
da_solar_pot = np.full((len(list_parents),len(list_members),3653),np.nan)
da_dayhours = np.full((len(list_parents),len(list_members),3653),np.nan)
da_cell_temp = np.full((len(list_parents),len(list_members),3653),np.nan)
da_tasday = np.full((len(list_parents),len(list_members),3653),np.nan)

# Loop over all ensemble members
for i_p,P in enumerate(list_parents):      # 16 parents
    for i_m,M in enumerate(list_members):   # 10 members
        print(f"- Loop: P = {P}, M = {M}")
        
        # Open LENTIS data
        print(f"  .open LENTIS data")
        da_tas_ensmem = open_data_LENTIS_ensmem('tas','day',EXP,P,M,pp_sel_point)['tas'].drop('height').load()
        print(f"    TAS loaded")
        da_tasmax_ensmem = open_data_LENTIS_ensmem('tasmax','day',EXP,P,M,pp_sel_point)['tasmax'].drop('height').load()
        print(f"    TASMAX loaded")
        da_rsds_ensmem = open_data_LENTIS_ensmem('rsds','day',EXP,P,M,pp_sel_point)['rsds'].load()
        print(f"    RSDS loaded")
        da_wind_ensmem = open_data_LENTIS_ensmem('sfcWind','day',EXP,P,M,pp_sel_point)['sfcWind'].drop('height').load()
        print(f"    SFCWIND loaded")

        # Compute impact variable
        print(f"  .compoute impact variable(s)")
        da_solar_pot_ensmem = compute_solar_energy_production(da_rsds_ensmem,da_tas_ensmem,da_tasmax_ensmem,da_wind_ensmem)
        # and some other variables for figure
        da_dayhours_ensmem = day_length(da_tas_ensmem)
        da_cell_temp_ensmem = solar_cell_temp(da_rsds_ensmem, da_tas_ensmem - kelvin, da_tasmax_ensmem - kelvin, da_wind_ensmem)
        da_tasday_ensmem = (da_tas_ensmem + da_tasmax_ensmem)/2 - kelvin

        # Store in one data array
        da_tas[i_p,i_m,:] = da_tas_ensmem
        da_tasmax[i_p,i_m,:] = da_tasmax_ensmem
        da_rsds[i_p,i_m,:] = da_rsds_ensmem
        da_wind[i_p,i_m,:] = da_wind_ensmem
        
        da_solar_pot[i_p,i_m,:] = da_solar_pot_ensmem
        da_dayhours[i_p,i_m,:] = da_dayhours_ensmem
        da_cell_temp[i_p,i_m,:] = da_cell_temp_ensmem
        da_tasday[i_p,i_m,:] = da_tasday_ensmem
        
        # Empty memory
        if not (P == list_parents[-1] and M == list_members[-1]):
            del da_tas_ensmem, da_tasmax_ensmem, da_rsds_ensmem, da_wind_ensmem
            del da_solar_pot_ensmem, da_dayhours_ensmem, da_cell_temp_ensmem, da_tasday_ensmem
        
        # Report time
        print("  .done at", datetime.now().strftime("%H:%M:%S"))
        
# Create xarray DataArray and DataSet
print(f"- Create proper xarray")
da_tas = xr.DataArray(da_tas,coords={'parent':list_parents,'member':list_members,'time':da_tas_ensmem.time.values},dims=['parent','member','time'],attrs=da_tas_ensmem.attrs,name='tas')
ds_energy_point = da_tas.to_dataset()
da_tasmax = xr.DataArray(da_tas,coords=da_tas.coords,dims=da_tas.dims,attrs=da_tasmax_ensmem.attrs)
ds_energy_point['tasmax'] = da_tasmax
da_rsds = xr.DataArray(da_rsds,coords=da_tas.coords,dims=da_tas.dims,attrs=da_rsds_ensmem.attrs)
ds_energy_point['rsds'] = da_rsds
da_wind = xr.DataArray(da_wind,coords=da_tas.coords,dims=da_tas.dims,attrs=da_wind_ensmem.attrs)
ds_energy_point['wind'] = da_wind

da_solar_pot = xr.DataArray(da_solar_pot,coords=da_tas.coords,dims=da_tas.dims)
da_solar_pot.attrs = {'long_name':'Solar energy potential', 'units':'fraction', 'history':'Computed using Example_solarenergy.py'}
ds_energy_point['PVpot'] = da_solar_pot
da_dayhours = xr.DataArray(da_dayhours,coords=da_tas.coords,dims=da_tas.dims)
da_dayhours.attrs = {'long_name':'Daylight hours', 'units':'h/d', 'history':'Computed using Example_solarenergy.py'}
ds_energy_point['dayhours'] = da_dayhours
da_cell_temp = xr.DataArray(da_cell_temp,coords=da_tas.coords,dims=da_tas.dims)
da_cell_temp.attrs = {'long_name':'Temperature of PV cell', 'units':'degC', 'history':'Computed using Example_solarenergy.py'}
ds_energy_point['PVcell_temp'] = da_cell_temp
da_tasday = xr.DataArray(da_tasday,coords=da_tas.coords,dims=da_tas.dims)
da_tasday.attrs = {'long_name':'Daytime average temperature', 'units':'degC', 'history':'Computed using Example_solarenergy.py'}
ds_energy_point['tasday'] = da_tasday

# Save to file
print(f"- Save to file")
if not one_by_one:
    ds_energy_point.to_netcdf(f"{output_directory}/energy_day_{EXP}_{da_tas_ensmem.lat.values:.1f}N_{da_tas_ensmem.lon.values:.1f}E.nc")
else:
    if len(list_members) == 1:
        ds_energy_point.to_netcdf(f"{output_directory}/energy_day_{EXP}_{da_tas_ensmem.lat.values:.1f}N_{da_tas_ensmem.lon.values:.1f}E_P{list_parents[0]}M{list_members[0]}.nc")
    else:
        ds_energy_point.to_netcdf(f"{output_directory}/energy_day_{EXP}_{da_tas_ensmem.lat.values:.1f}N_{da_tas_ensmem.lon.values:.1f}E_P{list_parents[0]}.nc")
        
    
    
