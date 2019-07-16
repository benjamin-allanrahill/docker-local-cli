#!/usr/bin/env python3\

# Low level module to run configurations in docker container 
# Benjamin Allan-Rahill

import subprocess, os.path, sys, socket
from colors import color
from eval import evalOrDie, yes_or_no, callWithPipe
from docker_container import Container

running_containers = []

def createAndRun(user, image="docker.rdcloud.bms.com:443/rr:Genomics2019-03_all", ports={'22': '2222', '8787': '8787'}, mode='d', keypath="/.ssh/", running_conts=[], label='bms'):
    running_containers= running_conts
    # check to see if the image is local
    if testImagePresence(image):
        print("You have this image on your machine")
        print("PORTS: ")
        print(ports)
        container = Container(image, ports=ports, label=label)
        
        # test to see if they already have one running
        if container.isImageRunning():
            print(f"You already have a container running with the image [{color(container.image, fg='blue')}]")
            y = yes_or_no("Do you want to create another container with the same image?")
            if not y:
                return
        else:
            print("No running containers of this image found. \nStarting new container")
        
        
        ## CHECK & CHANGE PORTS ##
        print("PORTS: ")
        print(container.ports)
        checkPorts(usedPorts(running_containers), container)


        ## START CONTAINER ##
        container.startContainer(mode)
        print(f"Your container is now running with ID: {container.cid}")
        #set up ssh
        sshSetup(container, keypath, user)
        #set up stash
        print("Trying to set up stash")
        setupStash(container)
        print(f"Access {color('Rstudio', fg='blue')} at {socket.gethostbyname(socket.gethostname())}:{container.ports['8787']}")

    ## PULL ##    
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

def setupStash(container,user):
    container.cpTo("./startup.py", "/tmp/")
    container.execute('chmod +x /tmp/startup.py')
    container.execute("python /tmp/startup.py")

    # TODO: Copy ssh keys 

def sshSetup(container, keypath, user):
    container.cpTo(f"{keypath}id_rsa", f"/home/domino/.ssh/id_rsa_{user}")
    container.cpTo(f"{keypath}id_rsa.pub", f"/home/domino/.ssh/id_rsa_{user}.pub")
    # append public key to authorized keys 
    container.execute(f"cat /home/domino/.ssh/id_rsa_{user}.pub >> /home/domino/.ssh/authorized_keys")

def usedPorts(container_list):
    used = []
    print(container_list)
    for c in container_list:
        print([port for key in c.ports.keys() for port in c.ports[key]])
        used += [c.ports[key] for key in c.ports.keys()]
    print("USED PORTS: ")
    print(used)
    return used

def checkPorts(allocated, container):
    for key in container.ports.keys():
        if container.ports[key] in allocated:
            print(f"The port {color(container.ports[key], fg='red')} is already allocated")
            print(color("Changing the port randomly now...", fg='yellow'))
            container.changePortsRand(allocated, key)



