#!/usr/bin/env python2

"""
Create CISM dSMB files for initMIP.

Note: the provided dSMB field is on the same Bamber grid as the 1km CISM grids.
      The coarser resolution dSMB files for CISM *should* be conservitively
      interpolated, but, since we are planning on a 1km final solution and only
      using a coarser resolution to work out the initialization method, we've
      only done a basic coarsening here.
"""

import os

from netCDF4 import Dataset

from util import ncfunc


base_reso = 1 # km

f_base = 'GIS.1km.InitCond.4Glissade.nc'
nc_base = ncfunc.get_nc_file(f_base, 'r')

f_ismip6 = 'dsmb_01B13_ISMIP6_v2.nc' 
nc_ismip6 = ncfunc.get_nc_file(f_ismip6, 'r')

f_name = 'GIS.1km.dSMB.4Glissade.nc'
idx = f_name.find('km')

base = ncfunc.DataGrid()

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


skips = [1,2,4,8] # reso == skips * base_reso
for  skip in skips:
    # setup coarsened data file
    coarse = ncfunc.DataGrid()

    coarse.ny = base.y[::skip].shape[0]
    coarse.nx = base.x[::skip].shape[0]
   
    f_coarse = f_name[:idx-1]+str(skip*base_reso)+f_name[idx:]

    nc_coarse = Dataset( f_coarse,'w' )
    nc_coarse.createDimension('time', None )
    nc_coarse.createDimension('y1', coarse.ny)
    nc_coarse.createDimension('x1', coarse.nx)
    nc_coarse.createDimension('y0', coarse.ny-1)
    nc_coarse.createDimension('x0', coarse.nx-1)
    nc_coarse.createDimension('level', base_level)
    nc_coarse.createDimension('lithoz', base_lithoz)
    nc_coarse.createDimension('staglevel', base_staglevel)
    nc_coarse.createDimension('stagwbndlevel', base_stagwbndlevel)


    coarse.time = nc_coarse.createVariable('time', 'd', ('time',))
    coarse.y    = nc_coarse.createVariable('y1',   'd', ('y1',)  )
    coarse.x    = nc_coarse.createVariable('x1',   'd', ('x1',)  )
    coarse.y0   = nc_coarse.createVariable('y0',   'd', ('y0',)  )
    coarse.x0   = nc_coarse.createVariable('x0',   'd', ('x0',)  )
    coarse.level = nc_coarse.createVariable('level',   'd', ('level',)  )
    coarse.lithoz = nc_coarse.createVariable('lithoz',   'd', ('lithoz',)  )
    coarse.staglevel = nc_coarse.createVariable('staglevel',   'd', ('staglevel',)  )
    coarse.stagwbndlevel = nc_coarse.createVariable('stagwbndlevel',   'd', ('stagwbndlevel',)  )

    ncfunc.copy_atts(base.y, coarse.y)
    ncfunc.copy_atts(base.x, coarse.x)
    ncfunc.copy_atts(base.y0, coarse.y0)
    ncfunc.copy_atts(base.x0, coarse.x0)
    ncfunc.copy_atts(base.level, coarse.level)
    ncfunc.copy_atts(base.lithoz, coarse.lithoz)
    ncfunc.copy_atts(base.staglevel, coarse.staglevel)
    ncfunc.copy_atts(base.stagwbndlevel, coarse.stagwbndlevel)

    coarse.time[0] = 0.
    coarse.y[:] = base.y[::skip]
    coarse.x[:] = base.x[::skip]
    coarse.y0[:] = base.y0[::skip]
    coarse.x0[:] = base.x0[:1-skip:skip]
    coarse.level[:] = base.level[:]
    coarse.lithoz[:] = base.lithoz[:]
    coarse.staglevel[:] = base.staglevel[:]
    coarse.stagwbndlevel[:] = base.stagwbndlevel[:]


    # make dSMB field
    coarse_dsmb = nc_coarse.createVariable('dsmb', 'd', ('time', 'y1', 'x1',))
    ismip6_dsmb = nc_ismip6.variables['DSMB']
    try:
        scale_factor = ismip6_dsmb.scale_factor
    except AttributeError:
        scale_factor = 1.0
    coarse_dsmb[0,:,:] = ismip6_dsmb[::skip,::skip]/scale_factor


    nc_coarse.close()
    os.chmod(f_coarse, 0o664) # uses an Octal number!

