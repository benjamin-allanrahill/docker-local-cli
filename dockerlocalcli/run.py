#!/usr/bin/env python3\

# Low level module to run configurations in docker container 
# Benjamin Allan-Rahill

import subprocess, os.path, sys, socket
from colors import color
from eval import evalOrDie, yes_or_no, callWithPipe
from docker_container import Container

def createAndRun(image="docker.rdcloud.bms.com:443/rr:Genomics2019-03_all", r_port='8787', mode='d', keypath="/.ssh/"):
    # check to see if the image is local
    if testImagePresence(image):
        print("You have this image on your machine")
        container = Container(image, r_port=r_port)
        
        # test to see if they already have one running
        if container.isImageRunning():
            print(f"You already have a container running with the image [{color(container.image, fg='blue')}]")
            return
        else:
            print("No running containers of this image found. \nStarting new container")
            container.startContainer(mode)
            print(f"Your container is now running with ID: {container.cid}")
            #set up ssh
            sshSetup(container, keypath)
            #set up stash
            print("Trying to set up stash")
            setupStash(container)
            print(f"Access {color('Rstudio', fg='blue')} at {socket.gethostbyname(socket.gethostname())}:{r_port}")
    else:
        pullImage(image)
        createAndRun(image)

def pullImage(image="docker.rdcloud.bms.com:443/rr:Genomics2019-03_all"):
    pull_cmd = f"docker pull {image}"
    print(f"Attempting to pull  image [{image}] from the registry")
    evalOrDie(pull_cmd, f"Failed to pull {image}. \nPlease make sure you are connected to the network. \n")
        
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
    find_tag_cmd = f"docker image ls | awk '$2==\"{tag}\" {{f  = 1}}; END {{ exit !f }}'"

    res, code = callWithPipe(find_tag_cmd, ignore=True)
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
     
def findSimilarImages(image):
    vals = image.split(':')
    registry = vals[0]
    port = vals[1].split('/')[0]
    repo = vals[1].split('/')[1]
    tag = vals[2]
    image = f"{registry}:{port}/{repo}"

    grep_cmd = f"docker images | grep {image} | awk '{{print $1; print $2; print $3}}'"

    # have to 'ignore' error codes when using grep so the program doesnt quit when no match is made
    res, code = callWithPipe(grep_cmd, "There was an error trying to find similar images")

    if res != '' and code == 0:
        info = res.replace('\n', ' ').split()
        print("Found these images under the same repository:")
        print(*(f"\t{info[i*3]}" for i in range(len(info) // 3)))
        answ = yes_or_no("would you like to run one of these? (y/n)")
        if answ:
            chooseImage()
    else:
        print("There were no similar images found")

def chooseImage(images):
    questions = [
        {
            'type': 'list',
            'name': 'image',
            'message': 'Which image do you want to run?',
            'choices': [images[i] for i in range(len(images))]
        }
    ]
    answers = prompt(questions)

def setupStash(container):
    container.cpTo("./startup.py", "/tmp/")
    container.execute('chmod +x /tmp/startup.py')
    container.execute("python /tmp/startup.py")

    # TODO: Copy ssh keys 

def sshSetup(container, keypath):
    container.cpTo(keypath, "/home/domino/.ssh/")
    # append public key to authorized keys 
    container.execute(f"cat {keypath}/id_rsa.pub >> /home/domino/.ssh/authorized_keys")