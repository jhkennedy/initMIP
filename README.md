Process:
--------

1) use the DIVA dycore for a temp. spin-up, starting with an initially linear
temperature profile, 

2) hold the geometry fixed during that spin-up 

3) subcycle the temperature calculation relative to the velocity calculation


-------------------------------------------------------------------------------


To avoid having the vel. field immediately get weird because of the linear temp.
profile, I suggest: first spinning up for 10 ka (?) without coupling between
the temperature and the rate factor.  This is a tiny bit tricky; it can be done
by setting "flow_factor" to 0 (const. rate factor), but won't work right
currently because "flwa" is not in the input .nc file (it would then default to
a value for isothermal ice, which we don't want).  I've set the .config up now
so that you can first do a single diagnostic solve (no evolution), and spit-out
the necessary "flwa" field as part of that output. Then, you can use that file
as a restart for this same config file, but switching "flow_law" from 2 to 0.
Now it will use a const.  rate factor but one that is realistic, based on the
old temps, and thus the vel field won't change as temps evolve.  Once the temp
evol. has used the current vel field for a few thousand years, we could switch
back to "flow_factor" = 2, to allow the vel. and temp. field to evolve
together.

--------------------------------------------------------------------------------

Steps:
------

1. Single diagnostic solve using `GIS.1km.InitCond.4Glissade.config` and `
GIS.1km.InitCond.4Glissade.nc`. 

2. Switch `flow_law` from `2` to `0` in `GIS.1km.InitCond.4Glissade.config` and
use (1.) output `*.nc` file for "a few thousand years" [lets go with 3]. 

3. Switch `flow_law` from `0` back to `2` in `GIS.1km.InitCond.4Glissade.config`
and use (2.) output `*.nc` file until ten thousand years have elapsed. 
