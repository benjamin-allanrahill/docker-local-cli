#!/usr/bin/env python3.6

# docker_local_cli.py
# high level script for CLI

import argparse, re, docker, platform
from colors import color
from locker.run import createAndRun
from locker.eval import callWithPipe, evalOrDie, yes_or_no
from locker.stop import stop
from locker.cleanup import cleanup
from locker.dropin import dropIn, sshIn
from locker.list import ps
from locker.files import add, grab

d = docker.from_env()

def main():

    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)

    subparsers = parser.add_subparsers(dest='subcommand', title='subcommands', help='Available sub-commands')
    
    run_parser = subparsers.add_parser('run', help='Run an environment on your local machine.')
    run_parser.add_argument('user', help='Your BMS username')
    run_parser.add_argument('-p','--ports', dest='ports', nargs=2, action='append', metavar=('inside', 'outside'), default=[['22', 2222],['8787', 8787]], help="[Optional] The ports you would like to use to run the servers on [ssh, RStudio server].")
    run_parser.add_argument('--env', '--image', dest='image', default='docker.rdcloud.bms.com:443/rr:Genomics2019-03_base', help='[Optional] The environment that you would like to run locally.')
    run_parser.add_argument('--keys', dest='keypath', help='[Optional] The location in which your SSH keys are stored.')
    run_parser.add_argument('-l','--label', dest='label', default='bms', help='[Optional] The metadata name to give the container')
    run_parser.add_argument('--mode', dest='mode', choices=['d', 'ti'], default='d', help='[Optional] Run the environment detached or interactive.')
    run_parser.add_argument('--cmd', dest='entrypoint', help='The command you would like to start in the container.')

    stop_parser = subparsers.add_parser('stop', help='Stop a running environment.')
    stop_parser.add_argument('--filter', dest='label', help="The meta data name that you would like to filter on EG: bms")
    stop_parser.add_argument('-a', '--all', dest='all', action='store_true', help='[Optional] Stop all the containers')
    stop_parser.add_argument('--halt', '--slam', dest='halt', default=False, action='store_true', help='[Optional] Force the stop of a running container (uses SIGKILL)')

    cleanup_parser = subparsers.add_parser('clean-up', help="Clean up running containers")
    cleanup_parser.add_argument('-a', '--all', dest='all', action='store_true', help='[Optional] Stop all the containers')
    cleanup_parser.add_argument('--container', metavar="ID", help="The container to add the files to")
    cleanup_parser.add_argument('-q', '--quiet', dest='quiet', default=False, action='store_true', help='[Optional] Don\'t prompt; just do.')

    dropin_parser = subparsers.add_parser('drop-in', help="Run a command inside the container")
    dropin_parser.add_argument('--cmd', dest='entrypoint', default='/bin/bash', help='The command you would like to start in the container.')
    dropin_parser.add_argument('--container', metavar="ID", help="The container to add the files to")
    dropin_parser.add_argument('--mode', dest='mode', choices=['d', 'ti'], default='ti', help='[Optional] Run the command detached or interactive.')

    ssh_parser = subparsers.add_parser('ssh', help="Ssh into a running container")
    ssh_parser.add_argument('--cmd', dest='entrypoint', default='/bin/bash', help='The command you would like to start in the container.')
    ssh_parser.add_argument('--container', metavar="ID", help="The container to add the files to")
    ssh_parser.add_argument('--mode', dest='mode', choices=['d', 'ti'], default='ti', help='[Optional] Run the command detached or interactive.')

    add_parser = subparsers.add_parser('add', help="Add a file or dir to the container")
    add_parser.add_argument('--container', metavar="ID", help="The container to add the files to")
    add_parser.add_argument('source', help='The local file')
    add_parser.add_argument('dest', help='Where you want the file to end up')

    grab_parser = subparsers.add_parser('grab ', help="Grab a file or dir from the container")
    grab _parser.add_argument('--container', metavar="ID", help="The container to grab the files from")
    grab _parser.add_argument('source', help='The path')
    grab _parser.add_argument('dest', help='Where you want the file to end up')

    list_parser = subparsers.add_parser('list', help="list all the running containers or images")
    list_parser.add_argument('-i', '--images', dest='images', action='store_true', help='[Optional] List the local images')
    list_parser.add_argument('-r', '--registry', dest='registry', default='docker.rdcloud.bms.com:443' help='[Optional] List the images at a registry')
    list_parser.add_argument('-a', '--all', dest='all', action='store_true', help='[Optional] List all the containers')

    args = parser.parse_args()

    if args.subcommand:
        cmd = args.subcommand.lower()
        
        # run the command
        #functions[cmd]
        if cmd == 'run':
            if args.keypath != None:
                keydir = args.keypath
            else:
                print("CHANGING TO DEFAULT PATH")
                keydir = defaultKeyPath(args.user)
            ports = parsePorts(args.ports)
            createAndRun(image=args.image, ports=ports, mode=args.mode, keypath=keydir, user=args.user, label={"name": args.label})
        elif cmd == 'stop':
            stop(getContainers(args), mode=args.halt)
        elif cmd == 'clean-up':
            yn = yes_or_no(f"This will {color('remove', fg='red')} your containers. Do you want to continue?")
            if not yn:
                exit(0)
            cleanup(getContainers(args, plusStopped=True), args.quiet)
        elif cmd == 'drop-in':
            dropIn(getContainers(args)[0], args.entrypoint, args.mode)
        elif cmd == 'ssh':
            sshIn(getContainers(args)[0], args.entrypoint, args.mode)            
        elif cmd == 'add':
            add(getContainers(args), args.source, args.dest)
        elif cmd == 'grab':
            grab(getContainers(args), args.source, args.dest)
        elif cmd == 'list':
            ps(args.all)



def getContainers(args, plusStopped=False):
    if hasattr(args, 'container') and args.container != None:
        return d.containers.get(args.container)
    elif hasattr(args, 'label') and args.label != None:
        print(args.label)
        print("Filtering containers")
        return d.containers.list(filters={'name': args.label}, all=plusStopped)
    elif hasattr(args, 'all') and args.all:
        print("ALL containers were specified")
        return d.containers.list(all=plusStopped)
    else:
        print("Only the last created container")
        return d.containers.list(limit=1, all=plusStopped)

def parsePorts(ports):
    # ports = ports.split(':')
    pdict = {}

    for pair in ports:
        pdict[f'{pair[0]}/tcp'] = int(pair[1])
    print(ports)
    print(pdict)

    return pdict

def defaultKeyPath(user):
    OS = platform.system()
    if OS == 'Windows':
        keypath = f'C:/Users/{user}/.ssh/'
    if OS == 'Darwin' or OS == 'Linux':
        keypath = f'~/.ssh/'
    print(f"the ssh path was changed to the deafult {OS} key path")
    return keypath
            
if __name__ == "__main__":
    main()