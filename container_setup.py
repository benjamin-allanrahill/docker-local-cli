#!/usr/bin/env python3\

# Low level module to run configurations in docker container 
# Benjamin Allan-Rahill

import subprocess, os.path, sys
from colors import color
from eval import evalOrDie, yes_or_no
from docker_container import Container

def createAndRun(image):
    # check to see if the image is local
    if testImagePresence(image):
        container = Container(image)
        
        # test to see if they already have one running
        if container.isRunning():
            print(f"You already have a container running with the image [{color(container.image, fg='blue')}]")
            pass
        print("No running containers of this image found. \nStarting new container")
        container.startContainer()
        print(f"Your container is now running with ID: {container.cid}")
    else:
        pullImage(image)
        createAndRun(image)

## JUST FOR TESTING!! ##
def testContainer(image):
    c = Container(image)
    print("Starting container")
    c.startContainer()
    print(f"Is the container running?  {c.isRunning()}")
    print("exec in!")
    c.execute('echo HELLO')
    c.cp('eval.py', '/tmp/eval.py')
    print("Going to remove container")
    c.remove()

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
    find_tag_cmd = f"docker images | awk '/$2=={tag}$/ {{f  = 1}}; END {{ exit !f }}'"


    res, code = evalOrDie(find_tag_cmd, ignore=True)
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
    res, code = evalOrDie(grep_cmd, "There was an error trying to find similar images")

    if res != '' and code == 0:
        info = res.replace('\n', ' ').split()
        print("Found these images under the same repository:" + * (f"\t{info[i*3]}" for i in range(len(info) // 3)))
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
            Separator('= IMAGES ='),
            'choices' = [images[i] for i in range(len(images))]
        }
    ]
    answers = prompt(questions)