#!/usr/bin/env python3\

# Low level module to run configurations in docker container 
# Benjamin Allan-Rahill

import subprocess, os, sys, socket, docker, platform, random 
from colors import color
from locker.eval import evalOrDie, yes_or_no, callWithPipe
from locker.utils import cpFrom, cpTo, execute
from locker.ssh import copyKeys
from locker.dropin import dropIn

running_containers = []

docker = docker.from_env()

def createAndRun(user, image, ports, mode, keypath, label, cap_add, devices):
    container = None
    # check to see if the image is local
    if testImagePresence(image):
        print("You have this image on your machine")

        # test to see if they already have one running
        if isImageRunning(image):
            print(f"You already have a container running with the image [{color(image, fg='cyan')}]")
            y = yes_or_no("Do you want to create another container with the same image?")
            if not y:
                return
            
            ## CHECK & CHANGE PORTS ##
            print("You will might need to change the ports ...")
            ports_new = checkPorts(usedPorts(), ports)
            ports = ports_new

        else:
            print("No running containers of this image found. \nStarting new container")

            # make sure the images exposed ports are allocated 
            ports = exposedPortsHelp(image)


        ## START CONTAINER ##
        container = docker.containers.run(  image=image,
                                            ports=ports,
                                            cap_add=cap_add,
                                            devices=devices,
                                            labels=label,
                                            detach=True)
        print(f"Your container is now running with ID: {container.id:.3f}")
        

        if label['registry'] == 'docker.rdcloud.bms.com:443':

            ## RUN BMS SPECIFIC ##

            ## COPY KEYS TO CONTAINER ##
            copyKeys(container, keypath, user)


            ## EXECUTE SETUP
            print("Trying to set up stash")
            setupStash(container, user)

            print(f"Access {color('Rstudio', fg='blue')} at http://{socket.gethostbyname(socket.gethostname())}:{ports['8787/tcp']}")
            print(f"Access {color('ssh', fg='yellow')} at http://{socket.gethostbyname(socket.gethostname())}:{ports['22/tcp']}")


    ## PULL ##    
    else:
        pullImage(image)
        createAndRun(image)
    
    ## EXEC IN ##
    if mode == 'ti':
        dropIn(container, '', 'ti')

def pullImage(image):
    pull_cmd = f"docker pull {image}"
    print(f"Attempting to pull  image [{image}] from the registry")
    evalOrDie(pull_cmd, f"Failed to pull {image}. \nPlease make sure you are connected to the network. \n")
        
def testImagePresence(image_name):
    if len(docker.images.list()) == 0:
        return False
    else:
        for image in docker.images.list():
            name = image.attrs['RepoTags'][0]
            if name == image_name:
                return True
            else:
                continue
        print("You do not have this image on your machine. I will now look for similar images...")
        return False
     
def findSimilarImages(image, registry):

    # if registry == 'bms':
    #     vals = image.split(':')
    #     registry = vals[0]
    #     port = vals[1].split('/')[0]
    #     repo = vals[1].split('/')[1]
    #     tag = vals[2]
    #     image = f"{registry}:{port}/{repo}"

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
        print("There were no similar images were found locally")

def setupStash(container, user):
    pwd = os.getcwd()

    # change directory to copy startup script
    swd = os.path.dirname(os.path.abspath(__file__))
    os.chdir(swd)

    cpTo(container, f"./startup.py", "/tmp/")
    execute(container, 'chmod +x /tmp/startup.py')
    execute(container, "sudo python /tmp/startup.py")
    
    #change back
    os.chdir(pwd)

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
            yn = yes_or_no("Would you like to change the ports manually?")
            if yn:
                new_port = changePortsManual(allocated, key)
            else:
                print(color("Changing the port randomly now...", fg='yellow'))
                new_port = changePortsRand(allocated, key, ports)
            ports[key] = new_port
    return ports 

def isImageRunning(image):
    for container in docker.containers.list():
        print(container.image)
        if container.attrs['Config']['Image'] == image:
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

def changePortsManual(used, inside):
    
    # TODO: test input to make sure 
    new_port = int(input(f"What would you like to set {inside} (in the container) to (on your machine)? [int > 1023]"))
    if new_port in used:
        print("That port is already allocated. Incrementing by one ...")
        new_port = int(new_port) + 1
    else:
        print(f"The new port for {inside} is: {new_port}")  
        return new_port

def exposedPortsHelp(image):
    print("EXPOSED PORTS")
    exp = docker.images.get(image).attrs['Config']['ExposedPorts']

    ports = {}
    for port in exp.keys():
        if exp[port] == {}:
            print("\nThis container has exposed ports that you have not allocated!")
            ports[port] = changePortsManual(usedPorts(), port)
        else:
            ports[port] = exp[port]
    
    return ports 

