#!/bin/bash
#PBS -A cli106ice
#PBS -q batch
#PBS -N GIS.8km.Const.4Albany.correction
#PBS -l walltime=01:00:00
#PBS -l nodes=40
#PBS -j oe
#PBS -m ae

# THE RUN COMMANDS:
cd /lustre/atlas1/cli106/proj-shared/initMIP/work/submit/fluxcor 
aprun -n 640 /lustre/atlas1/cli106/proj-shared/initMIP/cism-albany/builds/titan-gnu-felix/initmip/cism_driver/cism_driver /lustre/atlas1/cli106/proj-shared/initMIP/work/submit/fluxcor/GIS.8km.Const.4Albany.correction.config 

wait 
# FINISH
