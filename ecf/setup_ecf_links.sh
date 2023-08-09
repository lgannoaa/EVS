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

# AQM files
cd $ECF_DIR/scripts/aqm/stats
echo "Linking AQM stats ..."
cyc=$(seq 0 23)
link_master_to_cyc "jevs_aqm_stats_cyc" "$cyc"

echo "Done."
