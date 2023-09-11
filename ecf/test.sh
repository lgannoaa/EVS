#!/bin/bash

set -eu

ECF_DIR=$(pwd)

# Function that loop over forecast cycles and
# creates link between the master and target
function link_master_to_cyc(){
  tmpl=$1  # Name of the master template
  cycs=$2  # Array of cycles
  for cyc in ${cycs[@]}; do
    cycchar=$(printf %02d $cyc)
    master=${tmpl}_master.ecf
    target=${tmpl}_${cycchar}.ecf
    rm -f $target
    ln -sf $master $target
  done
}
cd $ECF_DIR/scripts/cam/stats
cyc=$(seq 0 6 23)
link_master_to_cyc "jevs_cam_namnest_snowfall_stats_cyc" "$cyc"
cyc=$(seq 0 6 23)
link_master_to_cyc "jevs_cam_hrrr_snowfall_stats_cyc" "$cyc"
cyc=$(seq 0 6 23)
link_master_to_cyc "jevs_cam_hireswfv3_snowfall_stats_cyc" "$cyc"
cyc=$(seq 0 6 23)
link_master_to_cyc "jevs_cam_hireswarw_snowfall_stats_cyc" "$cyc"
cyc=$(seq 0 6 23)
link_master_to_cyc "jevs_cam_hireswarwmem2_snowfall_stats_cyc" "$cyc"

