#!/bin/bash
###############################################################################
# Name of Script: exevs_rtofs_headline_plots.sh
# Purpose of Script: To create headline score plots for RTOFS forecast
#    verifications using MET/METplus.
# Author: L. Gwen Chen (lichuan.chen@noaa.gov)
###############################################################################

set -x

# set up plot variables
export PERIOD=last90days

# plot time series
export PTYPE=time_series

for lead in 000 024 048 072 096 120 144 168 192; do
  export FLEAD=$lead

# make plots for SST
  export VAR=SST
  export MASKS="GLB"

  for vcase in grid2grid grid2obs; do
    export VERIF_CASE=$vcase
    export LTYPE=SL1L2
    export THRESH=""

    if [ $vcase = 'grid2grid' ] ; then
      export OBTYPE=GHRSST
    fi

    if [ $vcase = 'grid2obs' ] ; then
      export OBTYPE=SFCSHP
    fi

    for stats in me rmse; do
      export METRIC=$stats
      $CONFIGevs/${VERIF_CASE}/$STEP/verif_plotting.rtofs.conf
    done

    export METRIC=fbias
    export LTYPE=CTC
    export THRESH=">=26.5"
    $CONFIGevs/${VERIF_CASE}/$STEP/verif_plotting.rtofs.conf
  done

# make plots for SIC
  export VAR=SIC
  export MASKS="Arctic"
  export VERIF_CASE=grid2grid
  export OBTYPE=OSISAF
  export METRIC=csi
  export LTYPE=CTC

  for thre in ">=15" ">=40" ">=80"; do
    export THRESH=$thre
    $CONFIGevs/${VERIF_CASE}/$STEP/verif_plotting.rtofs.conf
  done
done

# plot mean vs. lead time
export PTYPE=lead_average
export FLEAD="000,024,048,072,096,120,144,168,192"

# make plots for SST
export VAR=SST
export MASKS="GLB"

for vcase in grid2grid grid2obs; do
  export VERIF_CASE=$vcase
  export LTYPE=SL1L2
  export THRESH=""

  if [ $vcase = 'grid2grid' ] ; then
    export OBTYPE=GHRSST
  fi

  if [ $vcase = 'grid2obs' ] ; then
    export OBTYPE=SFCSHP
  fi

  for stats in me rmse; do
    export METRIC=$stats
    $CONFIGevs/${VERIF_CASE}/$STEP/verif_plotting.rtofs.conf
  done

  export METRIC=fbias
  export LTYPE=CTC
  export THRESH=">=26.5"
  $CONFIGevs/${VERIF_CASE}/$STEP/verif_plotting.rtofs.conf
done

# make plots for SIC
export VAR=SIC
export MASKS="Arctic"
export VERIF_CASE=grid2grid
export OBTYPE=OSISAF
export METRIC=csi
export LTYPE=CTC

for thre in ">=15" ">=40" ">=80"; do
  export THRESH=$thre
  $CONFIGevs/${VERIF_CASE}/$STEP/verif_plotting.rtofs.conf
done

# tar all plots together
tar -cvf $COMOUTplots/evs.plots.$COMPONENT.$RUN.$PERIOD.v$VDATE.tar $COMOUTplots/$RUN/*.png

exit

################################ END OF SCRIPT ################################
