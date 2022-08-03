## import packages
import xarray as xr
import numpy as np

## data locations
data_directory='/net/pc200272/nobackup/users/wiel/LENTIS/'
output_directory='/nobackup/users/wiel/LENTIS/datapaper/'

## define functions
def open_data_LENTIS(var,time,ensemble,preproc):
    """Open LENTIS ensemble data """
    if ensemble == 'PD': letter = 'h'
    elif ensemble == '2K': letter = 's'
    files = f"{data_directory}{ensemble}/{time}/{var}/{var}_{letter}*.nc"
    ds = xr.open_mfdataset(files,preprocess=preproc,combine='nested',concat_dim='ens',chunks=-1,parallel=True)
    return ds
def month_to_season(da,season):
    """Compute timeseries of seasonal means, note DJF is still JF...D"""
    if season == 'ann':
        # temporal weights
        month_length = da.time.dt.days_in_month
        weights_mon = month_length
        weights_season = weights_mon.groupby(weights_mon.time.dt.year).sum(dim='time')
        # mean (weighted by days in month)
        da_season = (da*weights_mon).groupby(da.time.dt.year).sum(dim='time') / weights_season
    elif season in ['DJF','JJA','MAM','SON']:
        # temporal weights
        month_length = da.time.dt.days_in_month
        weights_mon = month_length.sel(time=da.time.dt.season==season)
        weights_season = weights_mon.groupby(weights_mon.time.dt.year).sum(dim='time')
        # mean (weighted by days in month)
        da_sel = da.sel(time=da.time.dt.season==season)
        da_season = (da_sel*weights_mon).groupby(da_sel.time.dt.year).sum(dim='time') / weights_season
    # done
    return da_season
def area_mean(da):
    """Compute mean over lat/lon box"""
    # create weights
    weights_lat = np.cos(da.lat/180*np.pi).values
    weights_latlon = np.reshape(np.repeat(weights_lat,len(da.lon)),(len(da.lat),len(da.lon)))
    da_weights = xr.DataArray(weights_latlon,dims=['lat','lon'],coords=({'lat':da.lat,'lon':da.lon}),name='weights')
    # compute mean
    if da.notnull().any(): # remove NaN-gridcells
        total_weights = da_weights.where(da.notnull()).sum(dim={'lat','lon'})
    else:
        total_weights = da_weights.sum({'lat','lon'})
    area_mean = (da * da_weights).sum({'lat','lon'}) / total_weights
    return area_mean
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

## GOGOGOGO do computation
for EXP in ['PD','2K']:
    print('>> EXP =',EXP)

    # Open LENTIS data
    da_tas_mon = open_data_LENTIS('tas','Amon',EXP,None)['tas'].drop('height')
    da_tas_mon.load()
    print('da_tas_mon =', da_tas_mon.shape)
    
    # Monthly to annual data
    da_tas_y = month_to_season(da_tas_mon,'ann')
    print('da_tas_y =', da_tas_y.shape)

    # Compute global mean (create time series)
    da_gmst_y = area_mean(da_tas_y)
    print('da_gmst_y =', da_gmst_y.shape)

    # Compute linear trend (gmst time series, each ensemble member against time)
    da_gmst_y_slope,_ = linear_regression(da_gmst_y)
    print('da_gmst_y_slope =', da_gmst_y_slope.shape)
    # Compute linear trend (gmst time series, all ensemble members against time)
    da_gmst_y_slope_ens,_ = ensemble_linear_regression(da_gmst_y)
    print('da_gmst_y_slope_ens =', da_gmst_y_slope_ens.shape)

    # Compute linear trend (tas grid level, all ensemble members against time)
    da_tas_y_slope,_ = ensemble_linear_regression(da_tas_y)
    print('da_tas_y_slope =', da_tas_y_slope.shape)
    
    # Save to file
    da_gmst_y.name = 'gmst'
    ds_gmst = da_gmst_y.to_dataset()
    ds_gmst['gmst_slope'] = da_gmst_y_slope
    ds_gmst['gmst_ens_slope'] = da_gmst_y_slope_ens
    ds_gmst['tas_ens_slope'] = da_tas_y_slope
    ds_gmst.to_netcdf(f"{output_directory}/gmst_ann_trends_{EXP}.nc")
    
    # Empty memory
    del da_tas_mon, da_tas_y, da_gmst_y, da_tas_y_slope, ds_gmst

