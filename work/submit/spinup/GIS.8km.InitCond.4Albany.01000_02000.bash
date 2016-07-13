#!/bin/bash
#PBS -A cli106ice
#PBS -q batch
#PBS -N GIS.8km.InitCond.4Albany.01000_02000 
#PBS -l walltime=01:00:00
#PBS -l nodes=8
#PBS -j oe
#PBS -m ae

# THE RUN COMMANDS:
cd /lustre/atlas1/cli106/proj-shared/initMIP/work/submit/spinup 
aprun -n 128 /lustre/atlas1/cli106/proj-shared/initMIP/cism-albany/builds/titan-gnu-felix/initmip/cism_driver/cism_driver /lustre/atlas1/cli106/proj-shared/initMIP/work/submit/spinup/GIS.8km.InitCond.4Albany.01000_02000.config 

wait 
# FINISH
