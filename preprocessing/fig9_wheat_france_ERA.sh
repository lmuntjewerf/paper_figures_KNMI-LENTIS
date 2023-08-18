#!/bin/bash

set -ex

#-------------------
# calc wheat loss france in ERA
#-------------------


temp_dir=/usr/people/muntjewe/nobackup/nobackup_1/temp/

ERA_dir=/net/pc170547/nobackup_2/users/sager/ERA5/


for year in $(seq 1950 2021); do
  nextyear=$((year+1))

  tasmaxfiles=${ERA_dir}/${year}/day/era5_${year}1[012]_tmax.nc
  prfiles=${ERA_dir}/${nextyear}/day/era5_${nextyear}0[4567]_tp.nc

  #1 calc amount of days in OND with TASMAX between 0degC and 10degC
  cdo mergetime ${tasmaxfiles} ${temp_dir}/ERA_tasmax_OND_0.nc
  cdo setrtomiss,0,273.15  ${temp_dir}/ERA_tasmax_OND_0.nc ${temp_dir}/ERA_tasmax_OND_1.nc 
  cdo setrtomiss,283.15,500 ${temp_dir}/ERA_tasmax_OND_1.nc ${temp_dir}/ERA_tasmax_OND_2.nc
  cdo setmisstoc,0 ${temp_dir}/ERA_tasmax_OND_2.nc ${temp_dir}/ERA_tasmax_OND_3.nc
  cdo setrtomiss,273.15,283.15 ${temp_dir}/ERA_tasmax_OND_3.nc ${temp_dir}/ERA_tasmax_OND_4.nc
  cdo setmisstoc,1 ${temp_dir}/ERA_tasmax_OND_4.nc ${temp_dir}/ERA_tasmax_OND_5.nc
  cdo timsum ${temp_dir}/ERA_tasmax_OND_5.nc ${temp_dir}/${year}_ERA_OND_days.nc
  rm -rf ${temp_dir}/ERA_tasmax_OND_*.nc

  #2 calc daily avg precip in AMJJ 
  cdo mergetime ${prfiles} ${temp_dir}/ERA_pr_AMJJ_0.nc
  cdo timavg ${temp_dir}/ERA_pr_AMJJ_0.nc ${temp_dir}/${nextyear}_ERA_pr_AMJJ.nc
  rm -rf ${temp_dir}/ERA_pr_AMJJ_0.nc
done 

