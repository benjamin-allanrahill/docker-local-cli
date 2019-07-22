#!/usr/bin/env python3\

# Low level module to run configurations in docker container 
# Benjamin Allan-Rahill

import subprocess, os.path, sys, socket, docker, platform, random 
from colors import color
from eval import evalOrDie, yes_or_no, callWithPipe
from utils import cpFrom, cpTo, execute
from ssh import copyKeys

running_containers = []

docker = docker.from_env()

def createAndRun(user, image="docker.rdcloud.bms.com:443/rr:Genomics2019-03_all", ports={'22/tcp': 2222, '8787/tcp': 8787}, mode='d', keypath="/.ssh/", label={"name": "bms"}):
    
    # check to see if the image is local
    if testImagePresence(image):
        print("You have this image on your machine")
        print("PORTS: ")
        print(ports)

        ## CHECK & CHANGE PORTS ##
        ports_new = checkPorts(usedPorts(), ports)
        print("PORTS: ")
        print(ports_new)

        print("LABEL:")
        print(label)

        # test to see if they already have one running
        if isImageRunning(image):
            print(f"You already have a container running with the image [{color(image, fg='blue')}]")
            y = yes_or_no("Do you want to create another container with the same image?")
            if not y:
                return
        else:
            print("No running containers of this image found. \nStarting new container")


        ## START CONTAINER ##
        container = docker.containers.run(  image=image,
                                            ports=ports_new,
                                            cap_add=["SYS_ADMIN", "DAC_READ_SEARCH"],
                                            devices=["/dev/fuse"],
                                            labels=label,
                                            detach=True)
        print(f"Your container is now running with ID: {container.id}")
        
        # test execute cmd
        #execute(container, "/bin/bash")

        copyKeys(container, keypath, user)
        #set up ssh
        #sshSetup(container, keypath, user)
        #set up stash
        print("Trying to set up stash")
        setupStash(container, user)
        print(f"Access {color('Rstudio', fg='blue')} at {socket.gethostbyname(socket.gethostname())}:{ports['8787/tcp']}")

    ## PULL ##    
    else:
        #print(f"Attempting to pull  image [{image}] from the registry")
        #docker.images.pull(image)
        pullImage(image)
        createAndRun(image)

def pullImage(image="docker.rdcloud.bms.com:443/rr:Genomics2019-03_all"):
    pull_cmd = f"docker pull {image}"
    print(f"Attempting to pull  image [{image}] from the registry")
    evalOrDie(pull_cmd, f"Failed to pull {image}. \nPlease make sure you are connected to the network. \n")
        
def testImagePresence(image_name):

    image = docker.images.list()
    print(image)
    if len(image) == 0:
        return False
    else:
        return True
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

def setupStash(container, user):
    
    cpTo(container, "./startup.py", "/tmp/")
    execute(container, 'chmod +x /tmp/startup.py')
    execute(container,"sudo python /tmp/startup.py")

def usedPorts():
    print(docker.containers.list())
    used = []
    used += [val for c in docker.containers.list() for val in getPorts(c.id).values()]
    print("USED: ")
    print(used)
    return used
    

def getPorts(cid):
    print(f"CID: {cid}")
    docker_port_cmd = f'docker port {cid}'

    ports = evalOrDie(docker_port_cmd, "There was an error getting the ports")[0]
    port_dict = {}
    port_lines = ports.split('\n')
    #print(port_lines)
    for line in port_lines:
        if line != '':
            port = line.split('->')
            print(port)
            #print(port)
            c_port = port[0].rstrip()
            #print(c_port)
            l_port = port[1][9:]
            #print(l_port)
            port_dict[c_port] = int(l_port)

    print(port_dict)
    return port_dict

def checkPorts(allocated, ports):
    if allocated == []:
        return ports
    
    for key in ports.keys():
        if ports[key] in allocated:
            print(f"The port {color(ports[key], fg='red')} is already allocated")
            print(color("Changing the port randomly now...", fg='yellow'))
            new_port = changePortsRand(allocated, key, ports)
            ports[key] = new_port
    return ports 

def isImageRunning(image):
    for container in docker.containers.list():
        if container.image == image:
            return True
    return False

def changePortsRand(used, port, dict):
    print(dict[port])
    random_port = str(random.randint(3000, 9000))

    if random_port in used:
        random_port = int(random_port) + 1
    else:
        print(f"The new port for {port}/tcp is: {random_port}")  
        return random_port


