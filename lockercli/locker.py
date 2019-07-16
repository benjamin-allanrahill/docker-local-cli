#!/usr/bin/env python3.6

# docker_local_cli.py
# high level script for CLI

import argparse, re
from add import add
from cleanup import cleanup
from docker_container import Container
from dropin import dropIn
from run import createAndRun
from stop import stop
from eval import callWithPipe, evalOrDie

def main():

    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)

    subparsers = parser.add_subparsers(dest='subcommand', title='subcommands', help='Available sub-commands')
    
    run_parser = subparsers.add_parser('run', help='Run an environment on your local machine.')
    run_parser.add_argument('user', help='Your BMS username')
    run_parser.add_argument('--ports', dest='ports', nargs=2, default=['2222','8787'], help="[Optional] The ports you would like to use to run the servers on [ssh, RStudio server].")
    run_parser.add_argument('--env', '--image', dest='image', default='docker.rdcloud.bms.com:443/rr:Genomics2019-03_base', help='[Optional] The environment that you would like to run locally.')
    run_parser.add_argument('--keys', dest='keypath', default='~/.ssh/', help='[Optional] The location in which your SSH keys are stored.')
    run_parser.add_argument('--mode', dest='mode', choices=['d', 'ti'], default='d', help='[Optional] Run the environment detached or interactive.')
    run_parser.add_argument('--cmd', dest='entrypoint', help='The command you would like to start in the container.')

    stop_parser = subparsers.add_parser('stop', help='Stop a running environment.')
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

    add_parser = subparsers.add_parser('add', help="Add a file or dir to the container")
    add_parser.add_argument('--container', metavar="ID", help="The container to add the files to")
    add_parser.add_argument('source', help='The local file')
    add_parser.add_argument('dest', help='Where you want the file to end up')

    args = parser.parse_args()

    print(args)

    if args.subcommand:
        cmd = args.subcommand.lower()
        
        # run the command
        #functions[cmd]
        if cmd == 'run':
            createAndRun(image=args.image, ports={'22': args.ports[0], '8787': args.ports[1]}, mode=args.mode, keypath=args.keypath, user=args.user, running_conts=allContainers(plusStopped=False))
        elif cmd == 'stop':
            stop([getContainers(args)], mode=args.halt)
        elif cmd == 'clean-up':
            cleanup([getContainers(args, plusStopped=True)], args.quiet)
        elif cmd == 'drop-in':
            dropIn(getContainers(args), args.entrypoint, args.mode)
        elif cmd == 'add':
            add(args.source, args.dest, getContainers(args))


def getContainers(args, plusStopped=False):
    if hasattr(args, 'container') and args.container != None:
        return Container(cid=args.container)
    elif hasattr(args, 'all') and args.all:
        print("ALL containers were specified")
        return allContainers(plusStopped)
    else:
        print("Only the latest containers")
        return allContainers(plusStopped)[0]

def allContainers(plusStopped):
    cid_cmd = "docker ps -qa" if plusStopped else "docker ps -q"
    image_cmd = "docker ps -a | awk '{print $2}'" if plusStopped else "docker ps | awk '{print $2}'"
    created_cmd = "docker ps -a | awk '{print $4}" if plusStopped else "docker ps | awk '{print $4}'"
    
    cids = evalOrDie(cid_cmd, "There was an error getting container IDs")[0].split()
    images = callWithPipe(image_cmd, "There was an error getting the images", ignore=True)[0].split()[1:]
    print(images)
    #created = callWithPipe(created_cmd, "There was an error getting the creation data", ignore=True)[0].split()[1:]
    #print(created)
    #print(res)
    containers = [Container(cid=x) for x in cids]
    for i in range(len(containers)):
        containers[i].image = images[i]
        #containers[i].created = created[i]
        containers[i].ports = getPorts(containers[i].cid)

    return containers

def getPorts(cid):
    docker_port_cmd = f'docker port {cid}'

    ports = evalOrDie(docker_port_cmd, "There was an error getting the ports")[0]
    port_dict = {}
    port_lines = ports.split('\n')
    #print(port_lines)
    for line in port_lines:
        if line != '':
            port = line.split('->')
            #print(port)
            c_port = port[0].split('/')[0]
            #print(c_port)
            l_port = port[1][9:]
            #print(l_port)
            port_dict[c_port] = l_port

    return port_dict
            
if __name__ == "__main__":
    main()