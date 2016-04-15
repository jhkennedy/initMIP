"""
uitl.projections : Utilities to ease pojection transformations.

This module provides classes and functions to help transform projections. 

Class list:
    * DataGrid()

Functions list:
    * greenland(lc_bamber)
"""

import os
import numpy
import scipy
import pyproj

from util import speak


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

    def get_grid_corners(self):
        """
        This will create two array, size nx*4 and ny*4, which has the locations of the
        corners of each cell:
    
        [...; n_ia, n_ib, n_ic, n_id; ...]

        where a cell looks like:

        c ------- b
        |         |
        |   n_i   |
        |         |
        d ------- a
        """
        ady = self.y_grid-(self.dy/2.0)
        ady.shape = (self.nx*self.ny,1)
        bcy = self.y_grid+(self.dy/2.0)
        bcy.shape = (self.nx*self.ny,1)

        abx = self.x_grid+(self.dx/2.0)
        abx.shape = (self.nx*self.ny,1)
        cdx = self.x_grid-(self.dx/2.0)
        cdx.shape = (self.nx*self.ny,1)

        self.y_corners = numpy.concatenate( (ady, bcy, bcy, ady), axis=1) 
        
        self.x_corners = numpy.concatenate( (abx, abx, cdx, cdx), axis=1) 


    def make_stg_grid(self):
        """A way to make a basic grid from x,y data.
        """
        self.y0_grid, self.x0_grid = scipy.meshgrid(self.y0[:], self.x0[:], indexing='ij')
        self.dims = (self.ny0, self.nx0)
        self.dy0 = self.y0[1]-self.y0[0]
        self.dx0 = self.x0[1]-self.x0[0]
    
    def get_stg_grid_corners(self):
        """
        This will create two array, size nx0*4 and ny0*4, which has the locations of the
        corners of each cell:
    
        [...; n_ia, n_ib, n_ic, n_id; ...]

        where a cell looks like:

        c ------- b
        |         |
        |   n_i   |
        |         |
        d ------- a
        """
        ady = self.y0_grid-(self.dy0/2.0)
        ady.shape = (self.nx0*self.ny0,1)
        bcy = self.y0_grid+(self.dy0/2.0)
        bcy.shape = (self.nx0*self.ny0,1)

        abx = self.x0_grid+(self.dx0/2.0)
        abx.shape = (self.nx0*self.ny0,1)
        cdx = self.x0_grid-(self.dx0/2.0)
        cdx.shape = (self.nx0*self.ny0,1)

        self.y0_corners = numpy.concatenate( (ady, bcy, bcy, ady), axis=1) 
        
        self.x0_corners = numpy.concatenate( (abx, abx, cdx, cdx), axis=1) 



def greenland(lc_bamber):
    """The Bamber projection for Greenland.

    Parameters
    ----------
    lc_bamber :
        Location of the Bamber dataset.

    Returns
    -------
    proj_eigen_gl04c :
        A proj class instance that holds the Bamber DEM projection.
    """
    # basic latlon WGS84 datum
    proj_wgs84 = pyproj.Proj('+init=EPSG:4326')
    
    # EIGEN-GL04C referenced data:
    #----------------------------
    # unfortunately, bed, surface, and thickness data is referenced to 
    # EIGEN-GL04C which doesn't exist in proj4. However, EGM2008 should
    # be within ~1m everywhere (and within 10-20 cm in most places) so 
    # we use the egm08 projection which is available in proj4
    if not ( os.path.exists(lc_bamber+'/egm08_25.gtx') ):
        raise Exception("No "+lc_bamber+"/egm08_25.gtx ! Get it here: http://download.osgeo.org/proj/vdatum/egm08_25/egm08_25.gtx") 
    
    #NOTE: Bamber projection appears to not actually have any fasle northings or eastings. 
    #proj_eigen_gl04c = pyproj.Proj('+proj=stere +lat_ts=71.0 +lat_0=90 +lon_0=321.0 +k_0=1.0 +x_0=800000.0 +y_0=3400000.0 +geoidgrids='+path_bamber+'/egm08_25.gtx')
    proj_eigen_gl04c = pyproj.Proj('+proj=stere +lat_ts=71.0 +lat_0=90 +lon_0=321.0 +k_0=1.0 +geoidgrids='+lc_bamber+'/egm08_25.gtx')

    return (proj_eigen_gl04c, proj_wgs84)
