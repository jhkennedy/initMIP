# HPC PLATFORM DICTIONARIES
# =========================
# There should be a dictionary for each supported HPC platform which specifies 
# the default batch scheduler options to use. 
hopper_dict = {
        'PBS_A': 'm1795',
        'PBS_q': 'regular',
        'PBS_N': 'reg_test_all',
        'PBS_RES': 'mppwidth',
        'RES_NUM': '24',
        'PBS_walltime': '01:00:00',
        }


titan_dict = {
        'PBS_A': 'cli106ice',
        'PBS_q': 'batch',
        'PBS_N': 'reg_test_all',
        'PBS_RES': 'nodes',
        'RES_NUM': '1',
        'PBS_walltime': '01:00:00',
        }


# MAIN HPC DICTIONARY
# ===================
# Collection of all the HPC platform dictionaries. 
hpc_dict = {
        'titan': titan_dict,
        'hopper': hopper_dict,
        }


def create_job(args, job_name, p_replace, run_commands):
    """
    Create the job script for the HPC queues.
    """

    with open(job_name, 'w') as job_file:
        with open('util/job.template','r') as base_job: 
            for line in base_job:
                for src, target in p_replace.iteritems():
                    line = line.replace(src, target)
                job_file.write(line)

        job_file.write("\n")
        job_file.write("# THE RUN COMMANDS:\n")
        
        for command in run_commands:
            job_file.write(command)

        job_file.write("\nwait \n# FINISH\n")



