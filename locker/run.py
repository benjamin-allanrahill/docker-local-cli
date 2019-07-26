#!/usr/bin/env python3.6
"""
run.py
@description: Low level module to run configurations in docker container for the Locker sub command
@author: Benjamin Allan-Rahill

"""
import subprocess, os, sys, socket, docker, platform, random
from colors import color
from locker.eval import evalOrDie, yes_or_no, callWithPipe, detectTTY
from locker.utils import cpFrom, cpTo, execute
from locker.ssh import copyKeys
from locker.dropin import dropIn

running_containers = []

docker = docker.from_env()


def createAndRun(user, image, ports, mode, keypath, label, cap_add, devices):
    '''
        createAndRun(user, image, ports, mode, keypath, label, cap_add, devices)

        Create and run a docker container with specified parameters   
            
        Parameters
        ----------
        user: str
            user running container
        image: str
            name of docker image to run 
        ports: dict 
            port mappings 
        mode: str
            run interactive or detached 
        keypath: str 
            path to .ssh/ 
        label: dict
            labels to be added to the container
        cap_add: list
            linux capabilities for the container
        devices: list
            devices to add to the container

    '''
    container = None  # global container obj

    # check to see if the image is local
    if testImagePresence(image):

        print("You have this image on your machine")

        # test to see if they already have a container running
        if isImageRunning(image):
            print(
                f"You already have a container running with the image [{color(image, fg='cyan')}]"
            )
            if not yes_or_no(
                    "Do you want to create another container with the same image?"
            ):  # if "no"
                sys.exit()

            ## CHECK & CHANGE PORTS ##
            print("You will might need to change the ports ...")
            ports = checkPorts(usedPorts(), ports)

            ## CHECK EXPOSED PORTS ##
            ports = exposedPortsHelp(image, ports)

        else:  # no running containers of the image

            print(
                "No running containers of this image found. \nStarting new container"
            )

            # make sure the images exposed ports are allocated
            ports = exposedPortsHelp(image, ports)

        ## START CONTAINER ##
        
        if mode == 'ti' and label['registry'] == 'docker':  ## If it is a non-BMS image and the user is running -ti
            #print(ports)
            ports_str = " -p ".join([
                f"{ports[inside]}:{inside[:len(inside)-4]}"
                for inside in ports.keys()
            ])
            #print(ports_str)
            devices = [device.replace('/', '\/')for device in devices]
            cmd = (
                f"docker run -ti "
                f"{' -p ' + ports_str if len(ports) >0 else ''} "
                f" {'--cap-add=' + ' --cap-add='.join(cap_add) if len(cap_add)> 0 else ''} "
                #f" {'--device=' + ' --device='.join(devices) if len(devices)> 0 else ''} "
                f" --entrypoint bin/bash {image} ")

            # print(cmd)
            evalOrDie(cmd)
            #detectTTY(res)
            sys.exit()


        # regular run 
        container = docker.containers.run(image=image,
                                          ports=ports,
                                          cap_add=cap_add,
                                          devices=devices,
                                          labels=label,
                                          detach=True)

        print(f"Your container is now running with ID: {container.id}")

        if label['registry'] == 'docker.rdcloud.bms.com:443':  ## RUN BMS SPECIFIC SETUP

            ## COPY KEYS TO CONTAINER ##
            copyKeys(container, keypath, user)

            ## EXECUTE SETUP ##
            print("Trying to set up stash")
            setupStash(container, user)

            ## INSTRUCTIONS ##
            print(
                f"Access {color('Rstudio', fg='cyan')} at http://{socket.gethostbyname(socket.gethostname())}:{ports['8787/tcp']}"
            )
            print(
                f"Access {color('ssh', fg='yellow')} at http://{socket.gethostbyname(socket.gethostname())}:{ports['22/tcp']}"
            )
            if mode == 'ti':  # EXEC IN 
                execute(container, 'bin/bash', 'ti')


    else:  # image is not present locally

        ## PULL ##
        # TODO: Test connection before pulling
        pullImage(image)
        createAndRun(user=user,
                     image=image,
                     ports=ports,
                     mode=mode,
                     keypath=keypath,
                     cap_add=cap_add,
                     devices=devices,
                     label=label)

def pullImage(image):
    '''
        pullImage(image)

        Pull image using docker pull   
            
        Parameters
        ----------
        image: str
            name of docker image to run 
    '''

    pull_cmd = f"docker pull {image}"
    print(f"Attempting to pull  image [{image}] from the registry")
    evalOrDie(
        pull_cmd,
        f"Failed to pull {image}. \nPlease make sure you are connected to the network. \nMake sure that you have your HTTP_PROXY set if you are pulling from DockerHub. \n"
    )


def testImagePresence(image_name):
    '''
        testImagePresence(image_name)

        Test to see if image is present on the machine   
            
        Parameters
        ----------
        image_name: str
            name of docker image to run 

        Returns
        --------
        bool
            if the image is present

    '''

    if len(docker.images.list()) == 0:  # no images found at all
        return False
    else:
        for image in docker.images.list():
            name = image.attrs['RepoTags'][0]
            print(name)
            if name == image_name:
                return True
            else:
                continue
        print(
            "You do not have this image on your machine. I will now look for similar images..."
        )
        return False


## NOT IN USE ##
def findSimilarImages(image):
    '''
        findSimilarImages(image)

        Test to see if image is present on the machine   
            
        Parameters
        ----------
        image: str
            name of docker image to run

    '''

    grep_cmd = f"docker images | grep {image} | awk '{{print $1; print $2; print $3}}'"

    # have to 'ignore' error codes when using grep so the program doesnt quit when no match is made
    res, code = callWithPipe(
        grep_cmd, "There was an error trying to find similar images")

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
    '''
        setupStash(container, user)

        Utility function to setup /stash/ on the container   
            
        Parameters
        ----------
        container: Container
            container object to mount stash on

    '''

    pwd = os.getcwd()

    # change directory to copy startup script
    swd = os.path.dirname(os.path.abspath(__file__))
    os.chdir(swd)

    cpTo(container, f"./startup.py", "/tmp/")
    execute(container, 'chmod +x /tmp/startup.py')
    execute(container, f"sudo python /tmp/startup.py {user}")

    #change back
    os.chdir(pwd)


def usedPorts():
    containers = docker.containers.list()
    used = []
    used += [
        val for c in containers for val in getPorts(c.id).values()
        if len(containers) >= 1
    ]
    #print("USED: ")
    #print(used)
    return used


def getPorts(cid):
    #print(f"CID: {cid}")
    docker_port_cmd = f'docker port {cid}'

    ports = evalOrDie(docker_port_cmd,
                      "There was an error getting the ports")[0]
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

    #print(port_dict)
    return port_dict


def checkPorts(allocated, ports):
    if allocated == []:
        return ports

    for key in ports.keys():
        if ports[key] in allocated:
            print(
                f"The port {color(ports[key], fg='red')} is already allocated")
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
        #print(container.image)
        if container.attrs['Config']['Image'] == image:
            return True
    return False


def changePortsRand(used, port, dict):
    #print(dict[port])
    random_port = str(random.randint(3000, 9000))

    if random_port in used:
        random_port = int(random_port) + 1
    else:
        print(f"The new port for {port}/tcp is: {random_port}")
        return random_port


def changePortsManual(used, inside):

    # TODO: test input to make sure
    new_port = int(
        input(
            f"What would you like to set {inside} (in the container) to (on your machine)? [int > 1023]"
        ))
    if new_port in used:
        print("That port is already allocated. Incrementing by one ...")
        new_port = int(new_port) + 1
    else:
        print(f"The new port for {inside} is: {new_port}")
        return new_port


def exposedPortsHelp(image, ports):
    #print("EXPOSED PORTS")
    try:
        exp = docker.images.get(image).attrs['Config']['ExposedPorts']
    except KeyError as no_ports:
        # there are no exposed ports on the image
        return {}
    for port in exp.keys():
        #print(port)
        if port not in ports.keys():
            #print(ports.keys())
            print(
                "\nThis container has exposed ports that you have not allocated!"
            )
            if yes_or_no(f"Do you want to change port {port}?"):
                ports[port] = changePortsManual(usedPorts(), port)
            else:
                ports.pop(port, None)
    #print(ports)
    return ports
