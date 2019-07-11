#!/usr/bin/env python3\

# Low level module to run configurations in docker container 
# Benjamin Allan-Rahill

import subprocess, os.path, sys
from colors import color

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

def pullImage(image="docker.rdcloud.bms.com:443/rr:Genomics2019-03_all"):
    # check to see if the image is present
    if testImagePresence(image):
        pass
    else:
        pull_cmd = f"docker pull {image}"
        print(f"Attempting to pull  image [{image}] from the registry")
        _evalOrDie(pull_cmd, f"Failed to pull {image}. \nPlease make sure you are connected to the network. \n")
        
def testImagePresence(image_name):
    #get repo 
    vals = image_name.split(':')
    registry = vals[0]
    port = vals[1].split('/')[0]
    repo = vals[1].split('/')[1]
    tag = vals[2]
    image = f"{registry}:{port}/{repo}"
    print(f"REPO: {repo}")
    print(f"TAG: {tag}")
    find_tag_cmd = f"docker images | awk '2=={tag}'"


    res, code = _evalOrDie(find_tag_cmd, ignore=True)
    print(res, code)
    res = res.split()
    if code == 0:
        print(f"Found image [{color(image, fg='blue')}] with tag [{color(tag, fg='blue')}]")
        return True
    else:
        return False
        # TODO: Add check for other images 
        # search for repo images
        # grep_cmd = 
     
    

def _evalOrDie(cmd, msg="ERROR:", ignore=False):
        proc = subprocess.Popen(cmd, shell=True, stdout = subprocess.PIPE)
        stdout, stderr = proc.communicate()

        if proc.returncode != 0 and not ignore:
            print(color(msg, fg="yellow"))
            err_str = "COMMAND:\t {} \n\texited with exit value\t {} \n\twith output:\t {} \n\tand error:\t {}".format(cmd, proc.returncode, stdout, stderr)
            sys.exit(err_str)
            # sys.exit()

        return stdout, proc.returncode

# See here https://gist.github.com/garrettdreyfus/8153571 
def _yes_or_no(question):
    reply = str(raw_input(question+' (y/n): ')).lower().strip()
    if reply[:1] == 'y':
        return True
    if reply[:1] == 'n':
        return False
    else:
        return yes_or_no("Uhhhh... please enter ")