Last Update 1 February 2016: Version 2

The files in this directory contain the  surface mass balance (SMB) anomaly that
needs to be used for initMIP. The units are (meter ice equivalent/year) with an
assumed density of 910 kg/m^3 and 31556926 s/yr. This anomaly is schematic and
should not be considered as a realistic projection. The dataset was prepared by
Heiko Goelzer.

The core experiment duration is 100 years.

The SMB anomaly is to be implemented as a time dependent function, that takes
the form of a linear function which increases stepwise every full year (it is
therefore independent of the time step in the model): 

    SMB(t) = SMB_initialization + SMB_anomaly * (floor(t) / 40); for t in year from 0 to 40
    SMB(t) = SMB_initialization + SMB_anomaly * 1.0; for t > 40 years where
        SMB_anomaly is the anomaly provided by ISMIP6 and SMB_initialization is the SMB
        used for the initialization. 

A control run of the same time duration needs to also be submitted. The models
are run forward without any anomaly forcing, such that whatever surface mass
balance (SMB_initialization) was used in the initialization technique would
continue unchanged: 
    
    SMB(t) = SMB_initialization for all t

Note that no adjustment of SMB due to geometric changes in the experiments is
allowed (i.e. no elevation – SMB feedback!), to ensure that all models will
prescribe the same anomaly.

Modeling groups should use the 1km version of the SMB_anomaly to conservatively
interpolate to their model native grid. Files of lower resolution (5km, 10km,
and 20km) are provided for groups using a native grid based on Bamber et al.,
(2001). Please see the wiki for suggestion on how to conservatively interpolate.
Grid description files that work with CDO are provided for the 1, 5, 10, and
20km grids in the directory: 

    /ISMIP6/initMIP/grid_description_files/CDO 

SMB anomaly files made using Bamber Grid: 

    1km: dsmb_01B13_ISMIP6_v2.nc 
    5km: dsmb_05B13_ISMIP6_v2.nc 
    10km: dsmb_10B13_ISMIP6_v2.nc 
    20km: dsmb_20B13_ISMIP6_v2.nc

Grid description Files : 

    ISM_01km_CDO_file.txt 
    ISM_05km_CDO_file.txt
    ISM_10km_CDO_file.txt 
    ISM_20km_CDO_file.txt

