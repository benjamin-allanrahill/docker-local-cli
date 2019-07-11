#!/usr/bin/env python3\

# Low level module to run configurations in docker container 
# Benjamin Allan-Rahill

import colors, subprocess, os.path

def startContainer(image):
    docker_start_container = (
                               "docker run " 
                                "--cap-add=SYS_ADMIN " 
                                "--device=/dev/fuse " 
                                "--security-opt=apparmor:unconfined "
                                "--cap-add=DAC_READ_SEARCH "
                                "-d -p 2222:22 -p 8787:8787 "
                                f"{image}"
    )
    #print(docker_start_container)
    _evalOrDie(docker_start_container)

def pullImage(image="rr:Genomics2019-03_all"):

    pull_cmd = f"docker pull docker.rdcloud.bms.com:443/{image}"
    print(f"Attempting image [{image}] from the registry")
    _evalOrDie(pull_cmd, f"Failed to pull {image}. \nPlease make sure you are connected to the network. \n")

def _evalOrDie(cmd, msg="ERROR"):
    try:
        res = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        return res
    except subprocess.CalledProcessError as cmd_exp:
        print(colors.color(msg, fg='yellow'))
        print(colors.color(cmd_exp.output, fg='red'))