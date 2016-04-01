#!/usr/bin/env python2

"""
This script is used to structure the CISM output data for initMIP submission
"""

import os
import sys
import shutil
import argparse
import subprocess

from netCDF4 import Dataset

from util import ncfunc


# -------------------------------
# setup our input argument parser
# -------------------------------
parser = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

def abs_existing_file(file):
    file = os.path.abspath(file)
    if not os.path.isfile(file):
        print("Error! File does not exist: \n    "+file)
        sys.exit(1)
    return file

def abs_existing_dir(dir):
    dir = os.path.abspath(dir)
    if not os.path.isdir(dir):
        print("Error! Directory does not exist: \n    "+dir)
        sys.exit(1)
    return dir

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

def abs_creation_path(path):
    path = os.path.abspath(path)
    if not os.path.isdir(path):
        mkdir_p(path)
    return path

parser.add_argument('-w','--working-dir',default=os.path.join(os.getcwd(),"work"), type=abs_existing_dir,
        help="The directory the tests were run in.")
parser.add_argument('-s','--submit-dir',default=os.path.join(os.getcwd(),"submit"), type=abs_creation_path,
        help="The directory to stage the submission in.")


# ------------------
# Hard coded options
# ------------------
#NOTE: These should really be turned into options... 

# file structure will be:
#    GROUP/
#        MODEL/
#            EXP/
#               VAR_IS_GROUP_MODEL_EXP.nc
IS = 'GIS'
GROUP = 'ORNL'
MODEL = 'CISM1'

# datafile to massage
EXP = 'init'
f_base = 'GIS.8km.InitCond.4Albany.09000_10000.out.nc'

#EXP = 'ctrl'
#f_base = 'GIS.8km.Const.4Glissade.out.nc'

#EXP = 'asmb'
#f_base = 'GIS.8km.Test.4Glissade.out.nc'

file_root = '_'+'_'.join([IS, GROUP, MODEL, EXP])

# setup an output file
def setup_var_file(args, var_name, base):
    nc_var = Dataset( os.path.join(args.submit_dir, var_name+file_root+'.nc'),'w' )
    nc_var.createDimension('time', None )
    nc_var.createDimension('y', base.ny )
    nc_var.createDimension('x', base.nx )
    time_var = nc_var.createVariable('time', 'd', ('time',))
    if EXP == 'init':
        time_var[:] = 0
    else:
        time_var[:] = base.time[:]
    return nc_var
    

# ---------------
# main run script
# ---------------
def main():

    # import data file
    nc_base = ncfunc.get_nc_file(os.path.join(args.working_dir, f_base), 'r')
    
    base = ncfunc.DataGrid()

    base.time = nc_base.variables['time']
    
    base.y = nc_base.variables['y1']
    base.y0 = nc_base.variables['y0']
    base.ny = base.y[:].shape[0]

    base.x = nc_base.variables['x1']
    base.x0 = nc_base.variables['x0']
    base.nx = base.x[:].shape[0]

    base_level = 11
    base_lithoz = 20
    base_staglevel = 10
    base_stagwbndlevel = 12

    base.level = nc_base.variables['level']
    base.lithoz = nc_base.variables['lithoz']
    base.staglevel = nc_base.variables['staglevel']
    base.stagwbndlevel = nc_base.variables['stagwbndlevel']


    


    ###################
    # Get 2D variables:
    ###################
    # 2D variables as snapshots, every 5 years, starting at t=0
    # --------------------------------------------------------------------------
    # Variable (Dims)  |  Variable Name  |  Standard Name  |  Units  |  Comment 
    # --------------------------------------------------------------------------

    # Ice thickness (x,y,t)  |  lithk  |  land_ice_thickness  |  m  |  The thickness of the ice sheet
    base_var = 'thk' # (time, y1, x1)
    submit_var = 'lithk'
    nc_submit = setup_var_file(args, submit_var, base)
    sv = nc_submit.createVariable(submit_var, 'd', ('time', 'y','x',) )
    try:
        if EXP == 'init':
            sv[0,:,:] = nc_base.variables[base_var][-1,:,:] 
        else:
            sv[:,:,:] = nc_base.variables[base_var][:,:,:]
    except:
        pass
    nc_submit.close()

    # Surface elevation (x,y,t)  |  orog  |  surface_altitude  |  m  |  The altitude or surface elevation of the ice sheet
    base_var = 'usurf' # (time, y1, x1)
    submit_var = 'orog'
    nc_submit = setup_var_file(args, submit_var, base)
    sv = nc_submit.createVariable(submit_var, 'd', ('time', 'y','x',) )
    try:
        if EXP == 'init':
            sv[0,:,:] = nc_base.variables[base_var][-1,:,:] 
        else:
            sv[:,:,:] = nc_base.variables[base_var][:,:,:]
    except:
        pass
    nc_submit.close()


    # Bedrock elevation (x,y,t)  |  topg  |  bedrock_altitude  |  m  |  The bedrock topography
    base_var = 'topg' # (time, y1, x1)
    submit_var = 'topg'
    nc_submit = setup_var_file(args, submit_var, base)
    sv = nc_submit.createVariable(submit_var, 'd', ('time', 'y','x',) )
    try:
        if EXP == 'init':
            sv[0,:,:] = nc_base.variables[base_var][-1,:,:] 
        else:
            sv[:,:,:] = nc_base.variables[base_var][:,:,:]
    except:
        pass
    nc_submit.close()


    # Geothermal heat flux (x,y)  |  hfgeoubed  |  upward_geothermal_heat_flux_at_ground_level  |  W m-2  |  Geothermal Heat flux
    base_var = 'bheatflx' # (time, y1, x1)
    submit_var = 'hfgeoubed'
    nc_submit = setup_var_file(args, submit_var, base)
    sv = nc_submit.createVariable(submit_var, 'd', ('time', 'y','x',) )
    try:
        sv[0,:,:] = nc_base.variables[base_var][-1,:,:] 
    except:
        pass
    nc_submit.close()


    # Surface mass balance flux (x,y,t)  |  acabf  |  land_ice_surface_specific_mass_balance_flux  |  kg m-2 s-1  | Surface Mass Balance flux
    base_var = 'acab' # (time, y1, x1)
    submit_var = 'acabf'
    nc_submit = setup_var_file(args, submit_var, base)
    sv = nc_submit.createVariable(submit_var, 'd', ('time', 'y','x',) )
    try:
        if EXP == 'init':
            sv[0,:,:] = nc_base.variables[base_var][-1,:,:] 
        else:
            sv[:,:,:] = nc_base.variables[base_var][:,:,:]
    except:
        pass
    nc_submit.close()


    # Basal mass balance flux (x,y,t)  |  libmassbf  |  land_ice_basal_specific_mass_balance_flux  |  kg m-2 s-1  |  Basal mass balance flux
    base_var = 'bmlt' # (????)
    submit_var = 'libmassbf'
    nc_submit = setup_var_file(args, submit_var, base)
    sv = nc_submit.createVariable(submit_var, 'd', ('time', 'y','x',) )
    try:
        if EXP == 'init':
            sv[0,:,:] = nc_base.variables[base_var][-1,:,:] 
        else:
            sv[:,:,:] = nc_base.variables[base_var][:,:,:]
    except:
        pass
    nc_submit.close()


    # Ice thickness imbalance (x,y,t)  |  dlithkdt  |  tendency_of_land_ice_thickness  |  m s-1  |  dHdt
    base_var = 'dthckdtm' # (????) NOTE: Glide only
    submit_var = 'dlithkdt'
    nc_submit = setup_var_file(args, submit_var, base)
    sv = nc_submit.createVariable(submit_var, 'd', ('time', 'y','x',) )
    try:
        if EXP == 'init':
            sv[0,:,:] = nc_base.variables[base_var][-1,:,:] 
        else:
            sv[:,:,:] = nc_base.variables[base_var][:,:,:]
    except:
        pass
    nc_submit.close()


    # Surface velocity in x (x,y,t)  |  uvelsurf  |  land_ice_surface_x_velocity  |  m s-1  |  u-velocity at land ice surface
    base_var ='uvel' # (time, level, y0, x0)
                     # level = 0
    submit_var = 'uvelsurf'
    nc_submit = setup_var_file(args, submit_var, base)
    sv = nc_submit.createVariable(submit_var, 'd', ('time', 'y','x',) )
    try:
        if EXP == 'init':
            sv[0,:,:] = nc_base.variables[base_var][-1,0,:,:] 
        else:
            sv[:,:,:] = nc_base.variables[base_var][:,0,:,:]
    except:
        pass
    nc_submit.close()


    # Surface velocity in y (x,y,t)  |  vvelsurf  |  land_ice_surface_y_velocity  |  m s-1  |  v-velocity at land ice surface
    base_var ='vvel' # (time, level, y0, x0)
                     # level = 0
    submit_var = 'vvelsurf'
    nc_submit = setup_var_file(args, submit_var, base)
    sv = nc_submit.createVariable(submit_var, 'd', ('time', 'y','x',) )
    try:
        if EXP == 'init':
            sv[0,:,:] = nc_base.variables[base_var][-1,0,:,:] 
        else:
            sv[:,:,:] = nc_base.variables[base_var][:,0,:,:]
    except:
        pass
    nc_submit.close()


    # Surface velocity in z (x,y,t)  |  wvelsurf  |  land_ice_surface_upward_velocity |  m s-1  |  w-velocity at land ice surface 
    base_var ='wvel' # (????)
                     # level = 0
    submit_var = 'wvelsurf'
    nc_submit = setup_var_file(args, submit_var, base)
    sv = nc_submit.createVariable(submit_var, 'd', ('time', 'y','x',) )
    try:
        if EXP == 'init':
            sv[0,:,:] = nc_base.variables[base_var][-1,0,:,:] 
        else:
            sv[:,:,:] = nc_base.variables[base_var][:,0,:,:]
    except:
        pass
    nc_submit.close()


    # Basal velocity in x (x,y,t)  |  uvelbase  |  land_ice_basal_x_velocity  |  m s-1  |  u-velocity at land ice base
    base_var ='uvel' # (time, level, y0, x0)
                     # level = 11
    submit_var = 'uvelbase'
    nc_submit = setup_var_file(args, submit_var, base)
    sv = nc_submit.createVariable(submit_var, 'd', ('time', 'y','x',) )
    try:
        if EXP == 'init':
            sv[0,:,:] = nc_base.variables[base_var][-1,-1,:,:] 
        else:
            sv[:,:,:] = nc_base.variables[base_var][:,-1,:,:]
    except:
        pass
    nc_submit.close()


    # Basal velocity in y (x,y,t)  |  vvelbase  |  land_ice_basal_y_velocity  |  m s-1  |  v-velocity at land ice base
    base_var ='vvel' # (time, level, y0, x0)
                     # level = 11
    submit_var = 'vvelbase'
    nc_submit = setup_var_file(args, submit_var, base)
    sv = nc_submit.createVariable(submit_var, 'd', ('time', 'y','x',) )
    try:
        if EXP == 'init':
            sv[0,:,:] = nc_base.variables[base_var][-1,-1,:,:] 
        else:
            sv[:,:,:] = nc_base.variables[base_var][:,-1,:,:]
    except:
        pass
    nc_submit.close()



    # Basal velocity in z (x,y,t)  |  wvelbase  |  land_ice_basal_upward_velocity  |  m s-1  |  w-velocity at land ice base
    base_var ='wvel' # (????)
                     # level = 11
    submit_var = 'wvelbase'
    nc_submit = setup_var_file(args, submit_var, base)
    sv = nc_submit.createVariable(submit_var, 'd', ('time', 'y','x',) )
    try:
        if EXP == 'init':
            sv[0,:,:] = nc_base.variables[base_var][-1,-1,:,:] 
        else:
            sv[:,:,:] = nc_base.variables[base_var][:,-1,:,:]
    except:
        pass
    nc_submit.close()


    # Mean velocity in x (x,y,t)  |  uvelmean  |  land_ice_vertical_mean_x_velocity  |  m s-1  |  The vertical mean land ice velocity 
    #    is the average from the bedrock to the surface of the ice
    # average over levels in uvel

    # Mean velocity in y (x,y,t)  |  vvelmean  |  land_ice_vertical_mean_y_velocity  |  m s-1  |  The vertical mean land ice velocity 
    #    is the average from the bedrock to the surface of the ice
    # average over levels in vvel

    # Surface temperature (x,y,t)  |  litempsnic  |  temperature_at_ground_level_in_snow_or_firn  |  K  |  Ice temperature at surface
    base_var = 'tempstag' # (time, stagwbndlevel, y1, x1)
                          # stagwbndlevel = 0
                          # could also use 'surftemp' or 'temp'
    submit_var = 'litempsnic'
    nc_submit = setup_var_file(args, submit_var, base)
    sv = nc_submit.createVariable(submit_var, 'd', ('time', 'y','x',) )
    try:
        if EXP == 'init':
            sv[0,:,:] = nc_base.variables[base_var][-1,0,:,:] 
        else:
            sv[:,:,:] = nc_base.variables[base_var][:,0,:,:]
    except:
        pass
    nc_submit.close()



    # Basal temperature (x,y,t)  |  litempbot  |  land_ice_basal_temperature  |  K  |  Ice temperature at base
    base_var = 'tempstag' # (time, stagwbndlevel, y1, x1)
                          # stagwbndlevel = 11 or 12 ?
                          # could also use 'btemp' or 'temp'
    submit_var = 'litempbot'
    nc_submit = setup_var_file(args, submit_var, base)
    sv = nc_submit.createVariable(submit_var, 'd', ('time', 'y','x',) )
    try:
        if EXP == 'init':
            sv[0,:,:] = nc_base.variables[base_var][-1,-1,:,:] 
        else:
            sv[:,:,:] = nc_base.variables[base_var][:,-1,:,:]
    except:
        pass
    nc_submit.close()

    # Basal drag (x,y,t)  |  strbasemag  |  magnitude_of_land_ice_basal_drag  |  Pa  |  Magnitude of basal drag
    base_var = 'beta' # (time, y0, x0)
    submit_var = 'strbasemag'
    nc_submit = setup_var_file(args, submit_var, base)
    sv = nc_submit.createVariable(submit_var, 'd', ('time', 'y','x',) )
    try:
        if EXP == 'init':
            sv[0,:,:] = nc_base.variables[base_var][-1,:,:] 
        else:
            sv[:,:,:] = nc_base.variables[base_var][:,:,:]
    except:
        pass
    nc_submit.close()


    # Calving flux (x,y,t)  |  licalvf  |  land_ice_specific_mass_flux_due_to_calving  |  kg m-2 s-1  |  Loss of ice mass resulting 
    #    from iceberg calving. Only for grid cells in contact with ocean
    base_var = 'calving' # (????)
    submit_var = 'licalvf'
    nc_submit = setup_var_file(args, submit_var, base)
    sv = nc_submit.createVariable(submit_var, 'd', ('time', 'y','x',) )
    try:
        if EXP == 'init':
            sv[0,:,:] = nc_base.variables[base_var][-1,:,:] 
        else:
            sv[:,:,:] = nc_base.variables[base_var][:,:,:]
    except:
        pass
    nc_submit.close()


    # Land ice area fraction (x,y,t)  |  sftgif  |  land_ice_area_fraction  |  1  |  Fraction of grid cell covered by land ice 
    #    (ice sheet, ice shelf, ice cap, glacier)
    # iarea / total area? 


    # Grounded ice sheet area fraction (x,y,t)  |  sfrgrf  |  grounded_ice_sheet_area_fraction  |  1  |  Fraction of grid cell 
    #    covered by grounded ice sheet, where grounded indicates that the quantity correspond to the ice sheet that flows over bedrock 
    # iareag / total area? 

    # Floating ice sheet area fraction (x,y,t)  |  sftflf  |  floating_ice_sheet_area_fraction  |  1  |  Fraction of grid cell 
    #    covered by ice sheet flowing over seawater
    # iareaf / total area?


    ######################
    # Get scalar variables
    ######################
    # Scalar outputs (time average, yearly). If possible, the t=0 value should contain a one year time average of the last year 
    # of the initialization.
    # --------------------------------------------------------------------------
    # Variable (Dims)  |  Variable Name  |  Standard Name  |  Units  |  Comment 
    # --------------------------------------------------------------------------

    # Total ice mass (t)  |  lim  |  land_ice_mass  |  kg  |  spatial integration, volume times density
    #ivol (km^3)* rho_ice (kg/m^3)

    # Mass above floatation (t)  |  limnsw  |  land_ice_mass_not_displacing_sea_water  |  kg  |  spatial integration, volume times density

    # Grounded ice area (t)  |  iareag  |  grounded_land_ice_area  |  m^2  |  spatial integration

    # Floating ice area (t)  |  iareaf  |  floating_ice_shelf_area  |  m^2  |  spatial integration

    # Total SMB flux (t)  |  tendacabf  |  tendency_of_land_ice_mass_due_to_surface_mass_balance  |  kg s-1  |  spatial integration

    # Total BMB flux (t)  |  tendlibmassbf  |  tendency_of_land_ice_mass_due_to_basal_mass_balance  |  kg s-1  |  spatial integration

    # Total calving flux (t)  |  tendlicalvf  |  tendency_of_land_ice_mass_due_to_calving  |  kg s-1  |  spatial integration 



if __name__=='__main__':
    args = parser.parse_args()
    main()


