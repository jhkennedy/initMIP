#!/usr/bin/env python2

"""
Write CDO grid desciption files for the CISM grids.
"""

import os
import numpy
import scipy
import pyproj

from netCDF4 import Dataset

from util import ncfunc
from util import projections

# =======
# Options
# =======
f_base = '../Base/Glissade/GIS.4km.InitCond.4Glissade.nc'
lc_bamber = './util/'

std_cdo_name = 'ISM_04km_CDO_file.txt'
stg_cdo_name = 'ISM_04km_CDO_file.stg.txt'
bnd_cdo_name = 'ISM_04km_CDO_file.bnd.txt'

# ===================
# generate grid files
# ===================
nc_base = ncfunc.get_nc_file(f_base, 'r')

base = projections.DataGrid()

base.y = nc_base.variables['y1']
base.y0 = nc_base.variables['y0']
base.ny = base.y[:].shape[0]
base.ny0 = base.y0[:].shape[0]

base.x = nc_base.variables['x1']
base.x0 = nc_base.variables['x0']
base.nx = base.x[:].shape[0]
base.nx0 = base.x0[:].shape[0]

base.make_grid()
base.make_stg_grid()

base.get_grid_corners()
base.get_stg_grid_corners()

bamber_proj, latlon_proj = projections.greenland(lc_bamber)

class latlon():
    pass

latlon.x_grid, latlon.y_grid = pyproj.transform(bamber_proj, latlon_proj, base.x_grid.flatten(), base.y_grid.flatten())
latlon.x0_grid, latlon.y0_grid = pyproj.transform(bamber_proj, latlon_proj, base.x0_grid.flatten(), base.y0_grid.flatten())

latlon.x_corners, latlon.y_corners = pyproj.transform(bamber_proj, latlon_proj, base.x_corners.flatten(), base.y_corners.flatten())
latlon.y_corners = latlon.y_corners.reshape((base.ny*base.nx, 4))
latlon.x_corners = latlon.x_corners.reshape((base.ny*base.nx, 4))

latlon.x0_corners, latlon.y0_corners = pyproj.transform(bamber_proj, latlon_proj, base.x0_corners.flatten(), base.y0_corners.flatten())
latlon.y0_corners = latlon.y0_corners.reshape((base.ny0*base.nx0, 4))
latlon.x0_corners = latlon.x0_corners.reshape((base.ny0*base.nx0, 4))

with open(std_cdo_name,'w') as std:
    std.write('gridtype  = curvilinear\n')
    std.write('gridsize  = '+str(base.ny*base.nx)+'\n')
    std.write('xsize  = '+str(base.nx)+'\n')
    std.write('ysize  = '+str(base.ny)+'\n')
    
    std.write('xvals  = \n')
    numpy.savetxt(std, latlon.x_grid, fmt='%-4.8f')

    std.write('xbounds  = \n')
    numpy.savetxt(std, latlon.x_corners, fmt='%-4.8f')
 
    std.write('yvals  = \n')
    numpy.savetxt(std, latlon.y_grid, fmt='%-4.8f')

    std.write('ybounds  = \n')
    numpy.savetxt(std, latlon.y_corners, fmt='%-4.8f')


with open(stg_cdo_name,'w') as std:
    std.write('gridtype  = curvilinear\n')
    std.write('gridsize  = '+str(base.ny0*base.nx0)+'\n')
    std.write('xsize  = '+str(base.nx0)+'\n')
    std.write('ysize  = '+str(base.ny0)+'\n')
    
    std.write('xvals  = \n')
    numpy.savetxt(std, latlon.x0_grid, fmt='%-4.8f')

    std.write('xbounds  = \n')
    numpy.savetxt(std, latlon.x0_corners, fmt='%-4.8f')
 
    std.write('yvals  = \n')
    numpy.savetxt(std, latlon.y0_grid, fmt='%-4.8f')

    std.write('ybounds  = \n')
    numpy.savetxt(std, latlon.y0_corners, fmt='%-4.8f')


