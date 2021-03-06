#!/usr/bin/env python2

"""
Script to spin up Greenland for the initMIP initialization experiments
"""

#FIXME: So, CISM allows for multiple CF output sections in the config file inorder to
#       setup multiple output files (with their own frequency, and variables). However,
#       config parser does *not* allow multiple sections with the same name, so the second
#       one will over-ride the first. Config file has been edited to just dump everything
#       every step. This is SLOWWW.
#NOTE:  Will move to an annual ouput instead of every step once the full 100 years are 
#       able to be successfuly simulated. 

import os
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
        help="Run the spin-up. This will submit all the jobs, with each job held in the queue until the proceeding job"
        +"finishes successfully. If any are unsuccessful, all proceeding jobs will be removed.")
parser.add_argument('-w','--working-dir',default=os.path.join(os.getcwd(),"work"), type=abs_creation_path,
        help="The directory to run the spin-up in.")
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
spin_up_time = 10 # ka
cycle = 10 # a -- how often to run the velocity solve
input_time_slice = 11 # time slice to use on from input files. Note, for all input files, except the initial one

max_vel = 12 # km/a -- max velocity within the domain (for computing the cfl condition). 

grid_res = 8.0 # km

processors_use = 128
flow_law_switch_time = 3 # ka

job_dict = jobs.titan_dict
job_dict['RES_NUM'] = str(int(math.ceil(processors_use / 16.0)))
job_dict['PBS_walltime'] = '00:15:00'

# temerature solve to use:
#   0 = use air temp for column temps 
#   1 = prognostic
#   2 = hold temps. fixed at init. values
#   3 = enthalpy (untested)
which_temperature = 1

## ---------------------------
## Hard coded GLISSADE options
## ---------------------------
##NOTE: These should really be turned into options... 
#dycore = "Glissade"
#base_config = "./base/GIS.8km.InitCond.4Glissade.config"
#
## which_ho_approx to use, when:
##   2 = Blatter-Pattyn
##   4 = DIVA
#ho_approx_zeroth    = 2   # Just for the zeroth step
#ho_approx_temp_spin = 4   # for the first part where flow_law is constant (tempurate decoupled)
#ho_approx_coupled   = 4   # now tempurature and velocity is coupled
#
## Which preconditioner to use:
##    1 = diag. precond. (needed for use w/ DIVA)
##    2 = physics-based (SIA)
#precond_zeroth    = 2  # Just for the zeroth step
#precond_temp_spin = 1  # for the first part where flow_law is constant (tempurate decoupled)
#precond_coupled   = 1  # now tempurature and velocity is coupled
#
## how many iterations to allow (default = 100)
#glissade_iters = 200

# -------------------------
# Hard coded ALBANY options
# -------------------------
#NOTE: These should really be turned into options... 
dycore = "Albany"
base_config = "./base/GIS.8km.InitCond.4Albany.config"

# which_ho_approx to use, when:
#   2 = Blatter-Pattyn
#   4 = DIVA
ho_approx_zeroth    = 2   # Just for the zeroth step
ho_approx_temp_spin = 2   # for the first part where flow_law is constant (tempurate decoupled)
ho_approx_coupled   = 2   # now tempurature and velocity is coupled


# ---------------
# main run script
# ---------------
def main():

    base_path, base_name = os.path.split(abs_existing_file(base_config))
    base_root, base_ext = os.path.splitext(base_name)

    os.chmod(args.working_dir, 0o775) # uses an octal number!
    os.chdir(args.working_dir)

    CFL_condition = 0.5*(grid_res/max_vel) # a
    sub_cycles = int(math.ceil(cycle/CFL_condition))

    
    # setup CISM config files
    config_parser = ConfigParser.SafeConfigParser()
    config_parser.read(os.path.join(base_path,base_name))

    config_parser.set('time', 'dt', str(cycle))
    config_parser.set('time', 'subcyc', str(sub_cycles))
    
    config_root = base_root+"."+str(0).zfill(5)+"_"+str(0).zfill(5)
   
    shutil.copyfile(os.path.join(base_path, base_root+'.nc'), os.path.join(args.working_dir,config_root+'.nc') )
    os.chmod(os.path.join(args.working_dir,config_root+'.nc'), 0o664) # uses an octal number!
    if dycore == "Albany":
        shutil.copyfile(os.path.join(base_path,'input_albany-cism.xml'), os.path.join(args.working_dir,'input_albany-cism.xml') )
        os.chmod(os.path.join(args.working_dir,'input_albany-cism.xml'), 0o664) # uses an octal number!
        shutil.copyfile(os.path.join(base_path,'input_albany-cism.ILU.xml'), os.path.join(args.working_dir,'input_albany-cism.ILU.xml') )
        os.chmod(os.path.join(args.working_dir,'input_albany-cism.ILU.xml'), 0o664) # uses an octal number!

    config_parser.set('CF input', 'name', config_root+'.nc')
    config_parser.set('CF output', 'name', config_root+'.out.nc')
    config_parser.set('time', 'tstart', '%.1f' % 0)
    config_parser.set('time', 'tend', '%.1f' % 0)
    config_parser.set('options', 'flow_law', str(2))
    config_parser.set('options', 'temperature', str(which_temperature))
    config_parser.set('ho_options', 'which_ho_approx', str(ho_approx_zeroth)) 
    if dycore == "Glissade":
        config_parser.set('ho_options', 'which_ho_precond', str(precond_zeroth)) 
        config_parser.set('ho_options', 'glissade_maxiter', str(glissade_iters)) 


    # do the zero step.
    config_name = config_root+base_ext
    with open(os.path.join(args.working_dir,config_name), 'w') as config_file:
        config_parser.write(config_file)
    os.chmod(os.path.join(args.working_dir,config_name), 0o664) # uses an octal number!

    # make zero step job script
    run_commands = ["cd "+os.path.dirname(os.path.join(args.working_dir,config_name))+" \n",
                    "aprun -n "+str(processors_use)+" "+args.driver+" "+os.path.join(args.working_dir,config_name)+" \n"]
    job_name = config_root+".bash"
    job_dict['PBS_N'] = os.path.basename(config_root)
    
    jobs.create_job(args, job_name, job_dict, run_commands)

    if args.run:
        last_job_id = subprocess.check_output("qsub "+os.path.join(args.working_dir,job_name), shell=True)
        print(last_job_id.strip())

    
    # Now the rest of the steps
    config_parser.set('options', 'flow_law', str(0))
    #FIXME: NOT for albany
    #config_parser.set('options', 'restart', str(1))
    config_parser.remove_option('options', 'temp_init')
    config_parser.set('ho_options', 'which_ho_approx', str(ho_approx_temp_spin)) 
    if dycore == "Glissade":
        config_parser.set('ho_options', 'which_ho_precond', str(precond_temp_spin)) 
    
    job_dict['PBS_walltime'] = '01:00:00'
    for step in range(0,spin_up_time):
        if step == flow_law_switch_time:
            config_parser.set('options', 'flow_law', str(2))
            config_parser.set('ho_options', 'which_ho_approx', str(ho_approx_coupled)) 
            if dycore == "Glissade":
                config_parser.set('ho_options', 'which_ho_precond', str(precond_coupled)) 
        
        config_parser.set('CF input', 'name', config_root+'.out.nc')
        if step > 0:
            config_parser.set('CF input', 'time', str(input_time_slice))
        
        config_root = base_root+"."+str(step*1000).zfill(5)+"_"+str((step+1)*1000).zfill(5)
        config_parser.set('CF output', 'name', config_root+'.out.nc')
        config_parser.set('time', 'tstart', '%.1f' % float(step*1000))
        config_parser.set('time', 'tend', '%.1f' % float((step+1)*1000))
        
        config_name = config_root+base_ext
        with open(os.path.join(args.working_dir,config_name), 'w') as config_file:
            config_parser.write(config_file)
        os.chmod(os.path.join(args.working_dir,config_name), 0o664) # uses an octal number!
    
        # and the rest the job scripts
        run_commands = ["cd "+os.path.dirname(os.path.join(args.working_dir,config_name))+" \n",
                        "aprun -n "+str(processors_use)+" "+args.driver+" "+os.path.join(args.working_dir,config_name)+" \n"]
        job_name = config_root+".bash"
        job_dict['PBS_N'] = os.path.basename(config_root)
        
        jobs.create_job(args, job_name, job_dict, run_commands)
        
        if args.run:
            last_job_id = subprocess.check_output("qsub -W depend=afterok:"+last_job_id.strip()+" "+os.path.join(args.working_dir,job_name), shell=True)
            print(last_job_id.strip())

        


if __name__=='__main__':
    args = parser.parse_args()
    #FIXME: This is hacky, but it allows the default value to be type checked *after* the command line arguments are processed. 
    #       Argparse type checks the defaults immediately, before checking the command line argument. 
    #       Also, see the note at the to of the script, just after the `--driver` argument is added.
    if not args.driver:
        args.driver = abs_existing_file(os.path.join(os.getcwd(),"cism_driver"))
    main()
