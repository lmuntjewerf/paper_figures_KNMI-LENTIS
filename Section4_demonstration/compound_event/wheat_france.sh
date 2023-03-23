#!/bin/bash

set -ex

#-------------------
# calc wheat loss france
#-------------------


temp_dir=/usr/people/muntjewe/nobackup/nobackup_1/temp/

tasmax_dir=/usr/people/muntjewe/LENTIS/ec-earth/cmorised_by_var/hxxx/day/tasmax/
pr_dir=/usr/people/muntjewe/nobackup/nobackup_1/LENTIS/ec-earth/cmorised_by_var/hxxx/day/pr/
#pr_dir=/usr/people/muntjewe/nobackup/nobackup_1/VAREXdata/ec-earth/cmorised_by_var/hxxx/day/pr/


for i in {10..16}; do
 for j in {0..9}; do
  for year in $(seq 2000 2008); do
   nextyear=$((year+1))

   tasmaxfile=${tasmax_dir}/h"$(printf "%02d" $i)"${j}_day_tasmax/tasmax/gr/*/tasmax_day_EC-Earth3_historical_*_gr_${year}*-${year}*.nc
   prfile=${pr_dir}/h"$(printf "%02d" $i)"${j}_day_pr/pr/gr/*/pr_day_EC-Earth3_historical_*_gr_${nextyear}*-${nextyear}*.nc

   #1 calc amount of days in OND with TASMAX between 0degC and 10degC
   cdo setrtomiss,0,273.15  ${tasmaxfile} ${temp_dir}/tasmax_OND_0.nc
   cdo setrtomiss,283.15,500 ${temp_dir}/tasmax_OND_0.nc ${temp_dir}/tasmax_OND_1.nc
   cdo setmisstoc,0 ${temp_dir}/tasmax_OND_1.nc ${temp_dir}/tasmax_OND_2.nc
   cdo setrtomiss,273.15,283.15 ${temp_dir}/tasmax_OND_2.nc ${temp_dir}/tasmax_OND_3.nc
   cdo setmisstoc,1 ${temp_dir}/tasmax_OND_3.nc ${temp_dir}/tasmax_OND_4.nc
   cdo -L -timsum -selmon,10,11,12  ${temp_dir}/tasmax_OND_4.nc ${temp_dir}/${year}_h"$(printf "%02d" $i)"${j}_OND_days.nc
   rm -rf ${temp_dir}/tasmax_OND_*.nc

   #2 calc daily avg precip in AMJJ 
   #echo ${prfile}
   cdo -L -timavg -selmon,4,5,6,7 ${prfile} ${temp_dir}/${nextyear}_h"$(printf "%02d" $i)"${j}_pr_AMJJ.nc
  done
  cdo mergetime ${temp_dir}/*h"$(printf "%02d" $i)"${j}_OND_days.nc ${temp_dir}/h"$(printf "%02d" $i)"${j}_OND_days.nc
  cdo mergetime ${temp_dir}/*h"$(printf "%02d" $i)"${j}_pr_AMJJ.nc ${temp_dir}/h"$(printf "%02d" $i)"${j}_pr_AMJJ.nc 
 done
done 
