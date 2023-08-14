#!/bin/bash
###############################################################################
# Name of Script: exevs_rtofs_obs_prep.sh
# Purpose of Script: To pre-process OSI-SAF, NDBC, and Argo validation data.
# Author: L. Gwen Chen (lichuan.chen@noaa.gov)
#         Lin Gan (NCEP EMC EIB) upgrade serial cdo to parallel processing
###############################################################################

set -x

echo "***** CDO parallel processing DATA located in ${DATA}/parallel/cdo  *****"
CDO_pp=${DATA}/parallel/obs/cdo
if [ -d ${CDO_pp} ]; then rm -rf ${CDO_pp}; fi
mkdir -p ${CDO_pp}
CDO_pp_scr=${CDO_pp}/cdo_parallel.scr

# convert OSI-SAF data into lat-lon grid
export RUN=osisaf
mkdir -p $COMOUTprep/rtofs.$VDATE/$RUN

if [ -s $COMINobs/$VDATE/validation_data/seaice/osisaf/ice_conc_nh_polstere-100_multi_${VDATE}1200.nc ] ; then
  for ftype in nh sh; do
    echo "cdo remapbil,$FIXevs/rtofs_$RUN.grid \
    $COMINobs/$VDATE/validation_data/seaice/osisaf/ice_conc_${ftype}_polstere-100_multi_${VDATE}1200.nc \
    $COMOUTprep/rtofs.$VDATE/$RUN/ice_conc_${ftype}_polstere-100_multi_${VDATE}1200.nc" | tee -a ${CDO_pp_scr}
  done
  mpiexec -np 20 --cpu-bind verbose,core cfp ${CDO_pp_scr}
else
  export subject="OSI-SAF Data Missing for EVS RTOFS"
  echo "Warning: No OSI-SAF data was available for valid date $VDATE." > mailmsg
  echo "Missing file is $COMINobs/$VDATE/validation_data/seaice/osisaf/ice_conc_nh_polstere-100_multi_${VDATE}1200.nc." >> mailmsg
  cat mailmsg | mail -s "$subject" $maillist
fi

# convert NDBC *.txt files into a netcdf file using ASCII2NC
export RUN=ndbc
mkdir -p $COMOUTprep/rtofs.$VDATE/$RUN

if [ -s $COMINobs/$VDATE/validation_data/marine/buoy/activestations.xml ] ; then
  run_metplus.py -c $CONFIGevs/metplus_rtofs.conf \
  -c $CONFIGevs/grid2obs/$STEP/ASCII2NC_obsNDBC.conf
else
  export subject="NDBC Data Missing for EVS RTOFS"
  echo "Warning: No NDBC data was available for valid date $VDATE." > mailmsg
  echo "Missing files are located at $COMINobs/$VDATE/validation_data/marine/buoy/." >> mailmsg
  cat mailmsg | mail -s "$subject" $maillist
fi

# convert Argo basin files into a netcdf file using python embedding
export RUN=argo
mkdir -p $COMOUTprep/rtofs.$VDATE/$RUN

if [ -s $COMINobs/$VDATE/validation_data/marine/argo/atlantic_ocean/${VDATE}_prof.nc ] ; then
  run_metplus.py -c $CONFIGevs/metplus_rtofs.conf \
  -c $CONFIGevs/grid2obs/$STEP/ASCII2NC_obsARGO.conf
else
  export subject="Argo Data Missing for EVS RTOFS"
  echo "Warning: No Argo data was available for valid date $VDATE." > mailmsg
  echo "Missing file is $COMINobs/$VDATE/validation_data/marine/argo/atlantic_ocean/${VDATE}_prof.nc." >> mailmsg
  cat mailmsg | mail -s "$subject" $maillist
fi

exit

################################ END OF SCRIPT ################################
