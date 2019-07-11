#!/usr/bin/env python3\

# Low level module to run configurations in docker container 
# Benjamin Allan-Rahill

import colors, subprocess, os.path

def startContainter(image):
    docker_start_container =    f"docker run"  \
                                "--cap -add = SYS_ADMIN" \
                                "--device=/dev/fuse" \
                                "--security-opt=apparmor:unconfined" \
                                "--cap-add=DAC_READ_SEARCH" \
                                "-d -p 2222:22 -p 8787:8787" \
                                "{image}"

    _evalOrDie(docker_start_container)



def _evalOrDie(cmd, msg="ERROR"):
    try:
        res = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        return res
    except subprocess.CalledProcessError as cmd_exp:
        print(msg)
        print(colors.color(cmd_exp.output, fg='red'))