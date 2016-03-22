#!/usr/bin/env python2

"""
Script to run the greenland initialization experiments
"""

import os
import math
import argparse
import ConfigParser

from util import jobs

# -------------------------------
# setup our input argument parser
# -------------------------------
parser = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

def unsigned_int(x):
    """
    Small helper function so argparse will understand unsigned integers.
    """
    x = int(x)
    if x < 1:
        raise argparse.ArgumentTypeError("This argument is an unsigned int type! Should be an integer greater than zero.")
    return x

def abs_existing_file(file):
    file = os.path.abspath(file)
    if not os.path.isfile(file):
        print("Error! File does not exist: \n    "+file)
        sys.exit(1)
    return file

parser.add_argument('-d','--driver',default=os.getcwd()+os.sep+"cism_driver", type=abs_existing_file,
        help="The CISM driver.")
parser.add_argument('--max-vel',default=10.0,
        help="Maximum velocity, in km/year, within the domain (for computing the CFL condition).")
parser.add_argument('--grid-res',default=1.0,
        help="The CISM grid resolution in km.")
parser.add_argument('--cycle',default=10.0,
        help="How often to run the velocity solve in years.")


# ------------------
# Hard coded options
# ------------------
#NOTE: These should really be turned into options... 

spin_up_time = 10 # ka
#base_config = "./GIS.1km.InitCond.4Glissade.config"
#base_config = "./GIS.4km.InitCond.4Glissade.config"
base_config = "./GIS.8km.InitCond.4Glissade.config"
base_root, base_ext = os.path.splitext(base_config)

processors_use = 128
flow_law_switch_time = 3 # ka

job_dict = jobs.titan_dict
job_dict['RES_NUM'] = str(int(math.ceil(processors_use / 16.0)))
job_dict['PBS_walltime'] = '00:15:00'

# ---------------
# main run script
# ---------------
def main():

    CFL_condition = 0.5*(args.grid_res/args.max_vel) # a
    sub_cycles = int(math.ceil(args.cycle/CFL_condition))

    
    # setup CISM config files
    config_parser = ConfigParser.SafeConfigParser()
    config_parser.read(base_config)

    config_parser.set('time', 'dt', str(args.cycle))
    config_parser.set('time', 'subcyc', str(sub_cycles))
    
    config_root = base_root+"."+str(0).zfill(5)+"_"+str(0).zfill(5)
    config_parser.set('CF output', 'name', config_root+'.out.nc')
    config_parser.set('time', 'tstart', '%.1f' % 0)
    config_parser.set('time', 'tend', '%.1f' % 0)
    config_parser.set('options', 'flow_law', str(2))

    # do the zero step.
    config_name = config_root+base_ext
    with open(config_name, 'w') as config_file:
        config_parser.write(config_file)

    # make zero step job script
    run_commands = ["cd "+os.path.dirname(os.path.abspath(config_name))+" \n",
                    "aprun -n "+str(processors_use)+" "+args.driver+" "+os.path.abspath(config_name)+" \n"]
    job_name = config_root+".bash"
    job_dict['PBS_N'] = os.path.basename(config_root)
    
    jobs.create_job(args, job_name, job_dict, run_commands)
    
    # Now the rest of the steps
    config_parser.set('options', 'flow_law', str(0))
    job_dict['PBS_walltime'] = '01:00:00'
    for step in range(0,spin_up_time):
        if step == flow_law_switch_time:
            config_parser.set('options', 'flow_law', str(2))
        
        config_parser.set('CF input', 'name', config_root+'.out.nc')

        config_root = base_root+"."+str(step*1000).zfill(5)+"_"+str((step+1)*1000).zfill(5)
        config_parser.set('CF output', 'name', config_root+'.out.nc')
        config_parser.set('time', 'tstart', '%.1f' % float(step*1000))
        config_parser.set('time', 'tend', '%.1f' % float((step+1)*1000))
        
        config_name = config_root+base_ext
        with open(config_name, 'w') as config_file:
            config_parser.write(config_file)
    
        # and the rest the job scipts
        run_commands = ["cd "+os.path.dirname(os.path.abspath(config_name))+" \n",
                        "aprun -n "+str(processors_use)+" "+args.driver+" "+os.path.abspath(config_name)+" \n"]
        job_name = config_root+".bash"
        job_dict['PBS_N'] = os.path.basename(config_root)
        
        jobs.create_job(args, job_name, job_dict, run_commands)
        


if __name__=='__main__':
    args = parser.parse_args()
    main()
