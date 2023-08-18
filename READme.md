## Contents
This repo contains the scripts that were used for producing the figures, tables and number of the [KNMI-LENTIS datapaper](https://doi.org/10.5194/gmd-16-4581-2023). 

Muntjewerf, L., Bintanja, R., Reerink, T., and van der Wiel, K.: The KNMI Large Ensemble Time Slice (KNMI–LENTIS), Geosci. Model Dev., 16, 4581–4597, https://doi.org/10.5194/gmd-16-4581-2023, 2023.


### Section 2 - set-up
- **Figure 1. Overview of KNMI–LENTIS setup.**
(a) Global mean surface temperature (GMST) of the 16 ECE3p5 ensemble members forced
with CMIP6 historical and SSP2-4.5 forcing. Pink shading shows the two time slices in KNMI–LENTIS. (b) Part of the time slice setup.
From each of the 16 parent runs (grey), 10 KNMI–LENTIS simulations (pink) are branched using unique seeds to make a micro-perturbation
in the atmospheric initial conditions. (c) The full ensemble consists of two time slices of 10 years with 1600 years of data each: the present
day (PD) and present day C2K global warming (2 K). The parents are visualized by the grey (historical) and blue (SSP2-4.5) lines. The
KNMI–LENTIS simulations are visualized by the pink lines.


### Section 3 - limitations
- **Table 1. Temperature difference between the time slices.** 
Ensemble mean of the near-surface air temperature difference (K) between the
2K time slice and the PD time slice. The regions used to compute
Europe, North America, and South and Southeast Asia means are
shown in Fig. 2.
- **Table 2. Quantification of model bias w.r.t. ERA5 1991–2020.**
Ensemble mean of the near-surface air temperature bias (K) of
the KNMI–LENTIS present-day 2000–2009 time slice w.r.t. ERA5
1991–2020. The regions for Europe, North America, and South and
Southeast Asia are shown in Fig. 2.
- **Figure 2. Model bias.**
Near-surface air temperature bias (K) for the annual-average ensemble mean of the KNMI–LENTIS present-day time
slice [160 (2000–2009)] compared to ERA5 (1991–2020), for the (a) global, (b) Europe, (c) North America, and (d) South and Southeast
Asia regions. In panels (b)–(d) grid cells with a non-significant difference are dotted (p < 0:01).
- **Figure 3. Quantification of assumption 1:** 
Size of forced trends within a time slice. (a, c) Ensemble spread of annual mean values of global
mean surface temperature (GMST, shaded colours, percentile values denoted on the left). Ensemble interannual standard deviation and
ensemble linear trend of GMST over 10 years shown in bottom-right corner, including the 80% spread of this value for individual members.
The black bar in the centre shows the size of this linear trend relative to the ensemble spread. (b, d) Global map of the ratio between the
ensemble linear trend in near-surface temperature and the ensemble standard deviation in near-surface temperature. (a, b) The PD time slice.
(c, d) The 2K time slice.
- **Figure 4. Quantification of assumption 2:** 
Sampling internal variability within a time slice. (a) Distribution of daily 2m temperature (TAS)
data at 52.3 N, 4.9 E, in two halves of the PD ensemble (blue and green shading and lines, each based on 800 years) and 2K ensemble
(dotted red line, based on 1600 years). (b) GEV fit distribution (lines) and modelled data (dots) value plot for the warmest day of the year,
using the same colours as in (a).
- **Figure 5. Test of influence of parent on variability:**
Local TAS. (a) Time series, coloured by parent, of TAS at a grid point (52.3 N, 4.1 E)
for the first 31 d of the simulations. (b) Time series of variability (estimated as the standard deviation of TAS of all members with a certain
parent, then averaged over the parents) for different years in the time slice.
- **Figure 6. Test of influence of parent on variability:** 
Niño 3.4. (a) Distribution of the annual mean Niño 3.4 index, separated by parent and
simulation year. (b) Time series of variability (estimated as the standard deviation of Niño 3.4 of all members with a certain parent, then
averaged over the parents) throughout the time slice.

### Section 4 - demonstration
- **Figure 7. Ensemble climatology examples.**
For PD in blue and 2K in red: (a) return interval in years of surface snowmelt rates at the
eastern Greenland Ice Sheet grid point (72 N, 30 E); (b) scatter plot of total column-integrated soil moisture content and near-surface
temperature at the southern England grid point (51 N, 2 E) with the cloud mean as a dot and 2 standard deviations in the ellipse; and
(c) annual cycle of precipitation at the Horn of Africa grid point (8 N, 48 E). In (c), boxplots for the ensemble spread are defined as follows:
box, first quartile–median–third quartile (interquartile range (IQR)); bottom whisker, 􀀀1:5 IQR -– first quartile; top whisker, third quartile -– C1:5 IQR; outliers, values outside of these limits.
- **Figure 8. Hottest day in De Bilt, the Netherlands, in the PD ensemble.** 
(a) Europe maximum surface air temperature over Europe on the
hottest day (colours) and sea level pressure (contours every 5 hPa). (b) Surface energy balance components in De Bilt, the Netherlands,
during the days around the hottest day (pink shading) with the latent heat flux (hfls), sensible heat flux (hfss), downwelling shortwave
radiation (rsds), upwelling shortwave radiation (rsus), downwelling longwave radiation (rlds), and upwelling longwave radiation (rlus). The
date format is year-month-day. (c) Northern Hemisphere sea level pressure in colours and in contours every 5 hPa.
- **Figure 9. Example compound-event research.** 
Analysis of meteorological circumstances that lead to extreme wheat yield loss in France after
Ben-Ari et al. (2018). Presented values are the area average of the northern part of France (47–50 N, 0–7 E). (a) Scatter plot of number of
vernalizing days in autumn (October–December) versus daily average precipitation in spring of the next year (April–July). Large black dots
are ERA5 values (1950–2021), where 2016 is marked as a red dot. Small blue dots are KNMI–LENTIS PD values; horizontal and vertical
lines correspond to the average (solid lines) +/- 1 standard deviation (dotted lines). (b) Boxplots of the number of vernalizing days and the
daily average precipitation for both KNMI–LENTIS PD and ERA5.
- **Figure 10. Example ensemble climate-impact modelling.** 
(a) Scatter density plots showing the relationships between photovoltaics (PV) potential
and other variables in DJF and JJA. From left to right: incoming solar radiation, solar cell temperature, and daylight hours. (b) Example
time series of PV potential and incoming solar radiation. Triangles at the top show timing of annual maxima.
