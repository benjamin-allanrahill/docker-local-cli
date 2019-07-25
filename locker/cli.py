#!/usr/bin/env python3.6

"""
cli.py
@description: Top-level script for Local Docker CLI
@author: Benjamin Allan-Rahill

"""

import argparse, re, docker, platform, os.path, getpass, sys 
from colors import color
from locker.run import createAndRun
from locker.eval import callWithPipe, evalOrDie, yes_or_no
from locker.stop import stop
from locker.cleanup import cleanup
from locker.dropin import dropIn, sshIn
from locker.list import ps, listImages, listRegistry
from locker.files import add, grab

d = docker.from_env()

def parse_init():
    '''
        parse_init()

        determine version from init file   

        Returns
        -------
        list
            the version
    ''' 
    with open(os.path.join(config.HERE, '__init__.py')) as f: file_data = f.read()
    return [regex.search(file_data).group(2) for regex in (config.VERSION,) ]

def main():

    ROOT = defaultRootPath()
    USER = getpass.getuser()

    [version] = parse_init()

    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-V', '--version',  dest='version', action='store_true', help='print Locker CLI version')
    

    subparsers = parser.add_subparsers(     dest='subcommand', title='subcommands', help='Available sub-commands')
    
    add_parser = subparsers.add_parser('add',   help="Add a file or dir to the container")
    add_parser.add_argument('--container',      metavar="ID",    help="The container to add the files to")
    add_parser.add_argument('source',           help='The local file')
    add_parser.add_argument('dest',             type=str,       help='Where you want the file to end up')

    cleanup_parser = subparsers.add_parser('clean-up',  help="Clean up running containers")
    cleanup_parser.add_argument('-a', '--all',          dest='all',     action='store_true',    help='[Optional] Stop all the containers')
    cleanup_parser.add_argument('--container',          metavar="ID",   help="The container to add the files to")
    cleanup_parser.add_argument('-q', '--quiet',        dest='quiet',   default=False,          action='store_true', help='[Optional] Don\'t prompt; just do.')

    dropin_parser = subparsers.add_parser('drop-in',    help="Run a command inside the container")
    dropin_parser.add_argument('--cmd',                 dest='entrypoint',  default='/bin/bash',    help='The command you would like to start in the container.')
    dropin_parser.add_argument('--container',           metavar="ID",       help="The container to add the files to")
    dropin_parser.add_argument('--mode',                dest='mode',        choices=['d', 'ti'],    default='ti', help='[Optional] Run the command detached or interactive.')

    grab_parser = subparsers.add_parser('grab',     help="Grab a file or dir from the container")
    grab_parser.add_argument('--container',         metavar="ID", help="The container to grab the files from")
    grab_parser.add_argument('source',              help='The path')
    grab_parser.add_argument('dest',                help='Where you want the file to end up')

    list_parser = subparsers.add_parser('list',     help="list all the running containers or images")
    list_parser.add_argument('-a', '--all',         dest='all',         action='store_true',    help='[Optional] List all the containers')
    list_parser.add_argument('-i', '--images',      dest='images',      action='store_true',    help='[Optional] List the local images')
    list_parser.add_argument('-r', '--registry',    dest='registry',    nargs='?',              const='docker.rdcloud.bms.com:443', help='[Optional] List the images at a registry')

    run_parser = subparsers.add_parser('run',   help='Run an environment on your local machine.')
    run_parser.add_argument('--cap-add',        dest='cap_add',     nargs=1,    action='append',        default=["SYS_ADMIN", "DAC_READ_SEARCH"],   help='Add linux capabilities')
    run_parser.add_argument('--cmd',            dest='entrypoint',  help='The command you would like to start in the container.')
    run_parser.add_argument('--device',         dest='device',      nargs=1,    default=["/dev/fuse"],  help='Add device to the container')
    run_parser.add_argument('--env', '--image', dest='image',       default='docker.rdcloud.bms.com:443/rr:Genomics2019-03_base',                   help='[Optional] The environment that you would like to run locally.')
    run_parser.add_argument('--keys',           dest='keypath',     help='[Optional] The location in which your SSH keys are stored.')
    run_parser.add_argument('--label',          dest='labels',      nargs=2,    metavar=('key', 'val'), action='append',                            help='[Optional] A label to append to your container < key, val >')
    run_parser.add_argument('--mode',           dest='mode',        choices=['d', 'ti'], default='d',   help='[Optional] Run the environment detached or interactive.')
    run_parser.add_argument('-p','--ports',     dest='ports',       nargs=2,    action='append',        metavar=('inside', 'outside'),              default=[['22', 2222],['8787', 8787]], help="[Optional] The ports you would like to use to run the servers on [ssh, RStudio server].")
    #run_parser.add_argument('user', help='Your BMS username')

    ssh_parser = subparsers.add_parser('ssh',   help="Ssh into a running container")
    ssh_parser.add_argument('--cmd',            dest='entrypoint',  default='/bin/bash',    help='The command you would like to start in the container.')
    ssh_parser.add_argument('--container',      metavar="ID",       help="The container to add the files to")
    ssh_parser.add_argument('--mode',           dest='mode',        choices=['d', 'ti'],    default='ti', help='[Optional] Run the command detached or interactive.')

    stop_parser = subparsers.add_parser('stop',     help='Stop a running environment.')
    stop_parser.add_argument('-a', '--all',         dest='all',         action='store_true',    help='[Optional] Stop all the containers')
    stop_parser.add_argument('-r', '--registry',    dest='registry',    default='bms',          help='[Optional] Stop the images labeled with a particular registry')
    stop_parser.add_argument('--halt', '--slam',    dest='halt',        default=False,          action='store_true', help='[Optional] Force the stop of a running container (uses SIGKILL)')

    args = parser.parse_args()

    # --- version
    if args.version:
        print( 'Locker: Local Docker Version {}'.format(version) )

    # --- Subcommands
    if args.subcommand:
        cmd = args.subcommand.lower()

    # --- Run
        if cmd == 'run':
            if args.keypath != None:
                keydir = args.keypath
            else:
                #print("CHANGING TO DEFAULT PATH")
                keydir = ROOT + ".ssh/"
                print(keydir)
            ports = parsePorts(args.ports)
            createAndRun(image=args.image, ports=ports, mode=args.mode, keypath=keydir, user=USER, label=parseLabels(args.image, args.labels), cap_add=args.cap_add, devices=args.device)
        
    # --- Stop        
        elif cmd == 'stop':
            stop(getContainers(args), mode=args.halt)
        
    # --- clean-up        
        elif cmd == 'clean-up':
            yn = yes_or_no(f"This will {color('remove', fg='red')} your containers. Do you want to continue?")
            if not yn:
                exit(0)
            cleanup(getContainers(args, plusStopped=True), args.quiet)
        
    # --- drop-in        
        elif cmd == 'drop-in':
            dropIn(getContainers(args)[0], args.entrypoint, args.mode)
        
    # --- ssh        
        elif cmd == 'ssh':
            sshIn(getContainers(args)[0], args.entrypoint, args.mode)            
        
    # --- add        
        elif cmd == 'add':
            print(args.dest)
            add(getContainers(args)[0], ROOT + args.source, args.dest)
        
    # --- grab        
        elif cmd == 'grab':
            grab(getContainers(args)[0], args.source, ROOT+ args.dest)
        
    # --- list        
        elif cmd == 'list':
            if args.images:
                listImages()
            elif args.registry is not None:
                listRegistry(args.registry)
            else:
                ps(args.all)

def getContainers(args, plusStopped=False):
    '''
        getContainers(args, plusStopped=False)

        Get container objects by various methods   
            
        Parameters
        ----------
        args: Namespace
            arguments parsed from argparse
        plusStopped: bool
            wether to retrieve the stopped containers as well  

        Returns
        -------
        list
            the container objects asked for 
    ''' 
    _checkContainerL()
    if hasattr(args, 'container') and args.container != None:
        return d.containers.get(args.container)
    elif hasattr(args, 'label') and args.label != None:
        print(args.label)
        print("Filtering containers")
        return d.containers.list(filters={'registry': args.registry}, all=plusStopped)
    elif hasattr(args, 'all') and args.all:
        print("ALL containers were specified")
        return d.containers.list(all=plusStopped)
    else:
        print("Only the last created container")
        return d.containers.list(limit=1, all=plusStopped)

def parsePorts(ports):
    '''
        parsePorts(ports)

        Parse the ports specified by the user for runnning the container  
            
        Parameters
        ----------
        ports: list
            2D list with pairs of ports to specify KV pairs  

        Returns
        -------
        dict
            updated ports with kv pairs specified 
    ''' 
    pdict = {}

    for pair in ports:
        pdict[f'{pair[0]}/tcp'] = int(pair[1])
    print(ports)
    print(pdict)

    return pdict

def defaultRootPath():
        '''
        defaultRootPath()

        Determine the default root path (OS specific)

        Returns
        -------
        str
            default path of the root dir  
    ''' 
    USER = getpass.getuser()
    OS = platform.system()
    if OS == 'Windows':
        path = f'C:/Users/{USER}/'
    if OS == 'Darwin' or OS == 'Linux':
        path = '~/'
    #print(f"the root path was changed to the deafult {OS} key path")
    #print(path)
    return path

def parseLabels(image, labels):
    '''
        parseLabels(image, labels)

        Parse the labels specified by the user for runnning the container  
            
        Parameters
        ----------
        image: str
            the full name of the image 
        labels: list
            the 2D array specified by the user to determine kv pair labels to set on the container  

        Returns
        -------
        dict
            updated labels with kv pairs specified 
    ''' 
    if labels == None:
        return parseRegistry(image, {})
    labels_d = {}
    for key, val in labels:
        labels_d[key] = val
    parseRegistry(image, labels_d)
    return labels_d

def parseRegistry(image, labels):
    '''
        parseRegistry(image, labels)

        Determine which registry the image is from  
            
        Parameters
        ----------
        image: str
            the full name of the image 
        labels: dict
            the labels dictionary that are attached to the container 

        Returns
        -------
        dict
            updated labels with 'regsitry' kv pair specified 
    '''   
    result = re.match('^docker.rdcloud.bms.com:443', image)

    if result != None:
        labels['registry'] = 'docker.rdcloud.bms.com:443'
    else:
        labels['registry'] = 'docker'
    return labels

def _checkContainerL():
    '''
        _checkContainerL()

        Exit if no containers are running. 
    '''    
    containers = d.containers.list()
    print(containers)
    print(len(containers))
    if len(containers) == 0:
        print("You do not have any containers running...")
        sys.exit()

            
if __name__ == "__main__":
    main()