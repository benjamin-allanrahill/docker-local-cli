#!/usr/bin/env python3\

# docker_local_cli.py
# high level script for CLI

import argparse
from add import add
from cleanup import cleanup
from docker_container import Container
from dropin import dropIn
from run import createAndRun
from stop import stop
from eval import evalOrDie

def main():

    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)

    subparsers = parser.add_subparsers(dest='subcommand', title='subcommands', help='Available sub-commands')
    
    run_parser = subparsers.add_parser('run', help='Run an environment on your local machine.')
    run_parser.add_argument('--ports', dest='ports', default='8787', help="[Optional] The ports you would like to use to run the servers on.")
    run_parser.add_argument('--env', '--image', dest='image', default='docker.rdcloud.bms.com:443/rr:Genomics2019-03_base', help='[Optional] The environment that you would like to run locally.')
    run_parser.add_argument('--keys', dest='keyloc', default='/.ssh', help='[Optional] The location in which your SSH keys are stored.')
    run_parser.add_argument('--mode', dest='mode', choices=['d', 'ti'], default='d', help='[Optional] Run the environment detached or interactive.')
    run_parser.add_argument('--cmd', dest='entrypoint', help='The command you would like to start in the container.')

    stop_parser = subparsers.add_parser('stop', help='Stop a running environment.')
    stop_parser.add_argument('-a', '--all', dest='all', action='store_true', help='[Optional] Stop all the containers')
    stop_parser.add_argument('--halt', dest='halt', default=False, action='store_true', help='[Optional] Force the stop of a running container (uses SIGKILL)')

    cleanup_parser = subparsers.add_parser('clean-up', help="Clean up running containers")
    cleanup_parser.add_argument('-a', '--all', dest='all', action='store_true', help='[Optional] Stop all the containers')
    cleanup_parser.add_argument('-q', '--quiet', dest='quiet', default=False, action='store_true', help='[Optional] Don\'t prompt; just do.')

    dropin_parser = subparsers.add_parser('drop-in', help="Run a command inside the container")
    dropin_parser.add_argument('--cmd', dest='entrypoint', help='The command you would like to start in the container.')
    dropin_parser.add_argument('--mode', dest='mode', choices=['d', 'i'], default='d', help='[Optional] Run the command detached or interactive.')

    add_parser = subparsers.add_parser('add', help="Add a file or dir to the container")
    add_parser.add_argument('--container', default="latest", metavar="ID", help="The container to add the files to")
    add_parser.add_argument('source', help='The local file')
    add_parser.add_argument('dest', help='Where you want the file to end up')

    args = parser.parse_args()

    print(args)
    
    functions = {   'run': createAndRun(image=args.image, r_port=args.ports, mode=args.mode, keypath=args.keypath),
                    'stop': stop(getContainers(), args.halt),
                    'clean-up': cleanup(getContainers(), args.quiet),
                    'drop-in': dropIn(getContainers(), args.cmd, args.mode),
                    'add': add(args.source, args.dest, getContainers())
    }

    if args.subcommand:
        cmd = args.subcommand.lower()
        
        # run the command
        functions[cmd]


def getContainers():
    if args.container != '':
        return args.container
    elif args.all:
        print("ALL containers were specified")
        return allContainers()
    else:
        print("Only the latest containers")
        return allContainers()[0]

def allContainers():
    docker_ps_cmd = "docker ps -q"
    res, code = evalOrDie(docker_ps_cmd, "There was an error finding all the containers")

    print(res)
    containers = res.split()
    return containers
            
if __name__ == "__main__":
    main()