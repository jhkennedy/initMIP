"""
uitl.ncfunc : A set of useful functions when dealing with netcdf4 data.

This module provides functions to help deal with netCDF data. 

Class list:
    * DataGrid()

Functions list:
    * get_nc_file(fname, rw)
    * copy_att(fin, fout)
"""
import os
import scipy
import numpy as np
from netCDF4 import Dataset

class DataGrid():
    """A class to hold data grids.
    """
    
    def make_grid(self):
        """A way to make a basic grid from x,y data.
        """
        self.y_grid, self.x_grid = scipy.meshgrid(self.y[:], self.x[:], indexing='ij')
        self.dims = (self.ny, self.nx)
        self.dy = self.y[1]-self.y[0]
        self.dx = self.x[1]-self.x[0]

    def make_grid_flip_y(self):
        """A way to make a basic grid from x,y data, inverting y.
        """
        self.y_grid, self.x_grid = scipy.meshgrid(self.y[::-1], self.x[:], indexing='ij')
        self.dims = (self.ny, self.nx)
        self.dy = self.y[0]-self.y[1]
        self.dx = self.x[1]-self.x[0]


def get_nc_file(fname, rw) :
    """Get a netcdf file.
    """
    if os.path.exists(fname):
        nc_file = Dataset( fname, rw) 
    else:
        raise Exception("Can't find:  "+fname)
    return nc_file


def copy_atts(fin, fout) :
    """Copy netCDF attributes.

    This function copies the attributes from one netCDF element to another.
    
    Parameters
    ----------
    fin : 
        Source netCDF element
    fout :
        Target netCDF element

    Examples
    --------
    Copy the attributes from one variable to another.

    >>> old_var = nc_old.variables['old']
    >>> new_var = nc_new.createVariable('new', 'f4', ('y','x',) )
    >>> new_var[:,:] = old_var[:,:]
    >>> copy_atts( old_var,new_var )
    """
    
    # get a list of global attribute names from the incoming file
    atts = fin.ncattrs()
    
    # place those attributes in the outgoing file
    for ii in range(len(atts)) :
        fout.setncattr(atts[ii], fin.getncattr(atts[ii]))


