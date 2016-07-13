#!/usr/bin/env python2

"""
Script to run the Greenland initialization experiments for initMIP
"""

import os
import re
import sys
import math
import shutil
import argparse
import subprocess
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


#FIXME: This is hacky, but it allows the default value to be type checked *after* the command line arguments are processed. 
#       Also, see the note at the bottom of the script, just after the arguments are parsed.
parser.add_argument('-d','--driver', default=argparse.SUPPRESS, type=abs_existing_file,
        help="The CISM driver. (default: "+os.path.join(os.getcwd(),'cism_driver')+")")
parser.add_argument('-r','--run', action='store_true',
        help="Run the test. This will submit all the jobs, with each job held in the queue until the proceeding job"
        +"finishes successfully. If any are unsuccessful, all proceeding jobs will be removed.")
parser.add_argument('-w','--working-dir',default=os.path.join(os.getcwd(),"work"), type=abs_creation_path,
        help="The directory to run the test in.")
#FIXME: These are currently hard coded (as the same variable names without the
#       "args." prepended to it. When these are turned back on, make sure each variable
#       bellow has "args." prepended to it. 
#
#parser.add_argument('--max-vel',default=10.0,
#        help="Maximum velocity, in km/year, within the domain (for computing the CFL condition).")
#parser.add_argument('--grid-res',default=1.0,
#        help="The CISM grid resolution in km.")
#parser.add_argument('--cycle',default=10.0,
#        help="How often to run the velocity solve in years.")


# ------------------
# Hard coded options
# ------------------
#NOTE: These should really be turned into options... 
processors_use = 128

job_dict = jobs.titan_dict
job_dict['RES_NUM'] = str(int(math.ceil(processors_use / 16.0)))
job_dict['PBS_walltime'] = '02:00:00'


# ---------------------------
# Hard coded GLISSADE options
# ---------------------------
#NOTE: These should really be turned into options... 
dycore = "Albany"
const_config = "./base/GIS.8km.Const.4Albany.config"
const_path, const_name = os.path.split(abs_existing_file(const_config))
const_root, const_ext = os.path.splitext(const_name)

test_config = "./base/GIS.8km.Test.4Albany.config"
test_path, test_name = os.path.split(abs_existing_file(test_config))
test_root, test_ext = os.path.splitext(test_name)

dsmb_file = 'forcings/GIS.8km.dSMB.4Glissade.nc'

init_config = 'GIS.8km.InitCond.4Albany.09000_10000.config'


# ---------------
# main run script
# ---------------
def main():
    #TODO:
    # do the flux correction. 



    
    
    #TODO:
    #      Okay, here we need to take the init output file, copy it to another name,
    #      and for the "test" add in the acab_anomaly. 
    
    config_parser = ConfigParser.SafeConfigParser()
    config_parser.read(os.path.join(args.working_dir, init_config))
    which_temperature = config_parser.get('options', 'temperature')
    print(which_temperature)


    # setup const config file
    with open(os.path.join(const_path,const_name), 'r') as const_in:
        const_in_lines = const_in.readlines()
    
    
    # write the new config file
    with open(os.path.join(args.working_dir, const_name), 'w') as const_out:
        for line in const_in_lines:
            #TODO: change the input file to the one coppied above
            line = re.sub(r'^temperature = [0-9]', 'temperature = '+str(which_temperature), line)
            const_out.write(line)

    os.chmod(os.path.join(args.working_dir,const_name), 0o664) # uses an octal number!


    # setup test config file
    with open(os.path.join(test_path,test_name), 'r') as test_in:
        test_in_lines = test_in.readlines()
    
    
    # write the new config file
    with open(os.path.join(args.working_dir, test_name), 'w') as test_out:
        for line in test_in_lines:
            #TODO: change the input file to the one coppied above
            line = re.sub(r'^temperature = [0-9]', 'temperature = '+str(which_temperature), line)
            test_out.write(line)

    os.chmod(os.path.join(args.working_dir,test_name), 0o664) # uses an octal number!



    # make const job script
    run_commands = ["cd "+args.working_dir+" \n",
                    "aprun -n "+str(processors_use)+" "+args.driver+" "+os.path.join(args.working_dir,const_name)+" \n"]
    const_job_name = const_root+".bash"
    job_dict['PBS_N'] = os.path.basename(const_root)
    
    jobs.create_job(args, const_job_name, job_dict, run_commands)

    # make const job script
    run_commands = ["cd "+args.working_dir+" \n",
                    "aprun -n "+str(processors_use)+" "+args.driver+" "+os.path.join(args.working_dir,test_name)+" \n"]
    test_job_name = test_root+".bash"
    job_dict['PBS_N'] = os.path.basename(test_root)
    
    jobs.create_job(args, test_job_name, job_dict, run_commands)

    if args.run:
        const_job_id = subprocess.check_output("qsub "+os.path.join(args.working_dir,const_job_name), shell=True)
        print(const_job_id.strip())
        test_job_id = subprocess.check_output("qsub "+os.path.join(args.working_dir,test_job_name), shell=True)
        print(const_job_id.strip())

    

if __name__=='__main__':
    args = parser.parse_args()
    #FIXME: This is hacky, but it allows the default value to be type checked *after* the command line arguments are processed. 
    #       Argparse type checks the defaults immediately, before checking the command line argument. 
    #       Also, see the note at the to of the script, just after the `--driver` argument is added.
    if not args.driver:
        args.driver = abs_existing_file(os.path.join(os.getcwd(),"cism_driver"))
    main()
