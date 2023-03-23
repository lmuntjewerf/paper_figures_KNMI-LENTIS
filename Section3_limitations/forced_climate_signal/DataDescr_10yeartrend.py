## import packages
import xarray as xr
import numpy as np
import netCDF4

## data locations
data_directory='/net/pc200021/nobackup_1/users/muntjewe/LENTIS/'
output_directory='/nobackup/users/muntjewe/LENTIS/datapaper/'

## define functions
def open_data_LENTIS(var,time,ensemble,preproc):
    """Open LENTIS ensemble data """
    if ensemble == 'PD': letter = 'h'
    elif ensemble == '2K': letter = 's'
    files = f"{data_directory}{ensemble}/{time}/{var}/{var}_{letter}*.nc"
    ds = xr.open_mfdataset(files,preprocess=preproc,combine='nested',concat_dim='ens',chunks=-1,parallel=True)
    return ds

def open_one_LENTIS(var,time,ensemble,i,j):
    """Open one LENTIS data file from the ensemle"""
    if ensemble == 'PD': letter = 'h'
    elif ensemble == '2K': letter = 's'
    file=f"{data_directory}/{ensemble}/{time}/{var}/{var}_{letter}{str(i).zfill(2)}{str(j)}.nc"
    ds=xr.open_dataset(file)
    return ds

def linear_regression(da):
    """Simple linear regression"""
    # anomalies: data(y) & time(x)
    da_anom = da - da.mean(dim={'year'})
    time_anom = da.year - da.year.mean()
    # simple linear regression coefficients
    slope = (da_anom*time_anom).sum(dim={'year'}) / (time_anom*time_anom).sum(dim={'year'})
    intercept = da.mean(dim={'year'}) - slope * da.year.mean()
    return slope, intercept

def ensemble_linear_regression(da):
    """Simple linear regression, over all ensemble members"""
    # anomalies: data(y) & time(x)
    da_anom = da - da.mean(dim={'ens','year'})
    time_anom = da.year - da.year.mean()
    # simple linear regression coefficients
    slope = (da_anom*time_anom).sum(dim={'ens','year'}) / ((time_anom*time_anom).sum(dim={'year'})*len(da.ens))
    intercept = da.mean(dim={'ens','year'}) - slope * da.year.mean()
    return slope, intercept

def boxmean(da): 
    """
    Compute spatial weighted mean
    da      :  xarray DataArray
    """ 
    #weights = np.cos(np.deg2rad(da.lat)) 
    #weights.name = 'weights' 
    #boxmean = da.weighted(weights).mean(dim=('lat','lon')) 
    
    if hasattr(da, 'lat'):
        weights = np.cos(da.lat * np.pi / 180)
        boxmean = da.weighted(weights).mean(dim=('lat','lon')) 
    elif hasattr(da, 'latitude'):
        weights = np.cos(da.latitude * np.pi / 180)
        boxmean = da.weighted(weights).mean(dim=('latitude','longitude')) 
    return boxmean 

def ann_global_mean(ds_var):
    annual_global_mean = boxmean(ds_var).groupby('time.year').mean('time')
    return annual_global_mean
  
def ensemble_ann_avg_global_mean(var,time,ensemble):
    """Compute the annual-averaged, global weighted mean 
    for a given variable, for all ensemble members of a time slice"""
    ANN_avg_Global_mean=[]
    for i in np.arange(1,16+1):
        for j in np.arange(0,9+1):
            ds = open_one_LENTIS(var,time,ensemble,i,j)
            annual_global_mean = ann_global_mean(ds[var])
            ANN_avg_Global_mean.append(annual_global_mean)
            del ds,annual_global_mean
    return ANN_avg_Global_mean

def ensemble_linear_regression(var,time,ensemble):
    ENS_lin_reg_slope=[]
    ENS_lin_reg_intercept=[]
    for i in np.arange(1,16+1):
        for j in np.arange(0,9+1):
            ds = open_one_LENTIS(var,time,ensemble,i,j)
            slope, intercept = linear_regression(ds)
            ENS_lin_reg_slope.append(slope)
            ENS_lin_reg_intercept.append(intercept)
            del ds,slope,intercept
    return ENS_lin_reg_slope, ENS_lin_reg_intercept

def create_netcdf(ds,output_directory,ensemble):
    try: ncfile.close()  # just to be safe, make sure dataset is not already open.
    except: pass
    ncfile = netCDF4.Dataset(f"{output_directory}/gmst_ann_trends_{ensemble}_test.nc",mode='w',format='NETCDF4') 
    print(ncfile)

    year_dim = ncfile.createDimension('year', 10)     # year axis
    ens_dim = ncfile.createDimension('ens', None) # unlimited axis (can be appended to).

    year = ncfile.createVariable('year', np.float32, ('year',))
    year.units = 'year'
    year.long_name = 'year'
    ens = ncfile.createVariable('ens', np.float64, ('ens',))
    ens.units = 'member'
    ens.long_name = 'ensemble member'

    nyear = len(ds[0].coords['year'].values)
    # Write latitudes, longitudes.
    # # Note: the ":" is necessary in these "write" statements
    year[:] = ds[0].coords['year'].values

    # Define a 3D variable to hold the data
    gmst = ncfile.createVariable('gmst',np.float64,('ens','year')) # note: unlimited dimension is leftmost
    gmst.units = 'K' # degrees Kelvin
    gmst.standard_name = 'Global Mean Surface Temperature' # this is a CF standard name

    gmst[:,:] = ds_gmst_ens  # Appends data along unlimited dimension

    print(ncfile)
    ncfile.close()




## GOGOGOGO do computation

time='Amon'
var='tas'
for ensemble in 'PD','2K':
    print('starting')
    # Compute global mean (series)
    ds_gmst_ens = ensemble_ann_avg_global_mean(var,time,ensemble)
    print('ds_gmst_ens done')
    
    # Save to file
    create_netcdf(ds_gmst_ens,output_directory,ensemble)
    print('Done and saved to netcdf here: '+ output_directory)
    
    # Empty memory
    del ds_gmst_ens #, ds_gmst #da_gmst_slope, da_gmst_slope_ens, 


    ## Compute linear trend (gmst time series, each ensemble member against time)
    #da_gmst_slope,_ = linear_regression(ds_gmst_ens)
    #print('da_gmst_y_slope done')
    
    # Compute linear trend (gmst time series, all ensemble members against time)
    #da_gmst_slope_ens,_ = ensemble_linear_regression(var,time,ensemble)
    #print('da_gmst_y_slope_ens =', da_gmst_slope_ens.shape)


    #ds_gmst['gmst_slope'] = da_gmst_slope
    #ds_gmst['gmst_ens_slope'] = da_gmst_slope_ens
    #ds_gmst.to_netcdf(f"{output_directory}/gmst_ann_trends_{ensemble}.nc")




