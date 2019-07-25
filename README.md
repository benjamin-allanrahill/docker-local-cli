# docker_local_cli

> This is a command line tool to run docker environments locally 
> 
> Benjamin Allan-Rahill, Intern
> benjamin.allan-rahill@bms.com

![Logo](./logo.jpg?raw=True "Title")



## Installation

1. Clone this repo 

```bash
    git clone <"url">
```

2. Navigate to the directory


```bash
    cd docker_local_cli
```

3. Install 

```bash
    python3 -m pip3 install .
```

## Usage

```
$ locker -h

usage: locker [-h] {run,stop,clean-up,drop-in,ssh,add,grab,list} ...

optional arguments:
  -h, --help            show this help message and exit

subcommands:
  {run,stop,clean-up,drop-in,ssh,add,grab,list}
                        Available sub-commands
    run                 Run an environment on your local machine.
    stop                Stop a running environment.
    clean-up            Clean up running containers
    drop-in             Run a command inside the container
    ssh                 Ssh into a running container
    add                 Add a file or dir to the container
    grab                Grab a file or dir from the container
    list                list all the running containers or images
```

## Quick start

```
$ locker run

usage: locker run [-h] [--cap-add CAP_ADD] [--cmd ENTRYPOINT]
                  [--device DEVICE] [--env IMAGE] [--keys KEYPATH]
                  [--label key val] [--mode {d,ti}] [-p inside outside]

optional arguments:
  -h, --help            show this help message and exit
  --cap-add CAP_ADD     Add linux capabilities
  --cmd ENTRYPOINT      The command you would like to start in the container.
  --device DEVICE       Add device to the container
  --env IMAGE, --image IMAGE
                        [Optional] The environment that you would like to run
                        locally.
  --keys KEYPATH        [Optional] The location in which your SSH keys are
                        stored.
  --label key val       [Optional] A label to append to your container < key,
                        val >
  --mode {d,ti}         [Optional] Run the environment detached or
                        interactive.
  -p inside outside, --ports inside outside
                        [Optional] The ports you would like to use to run the
                        servers on [ssh, RStudio server].
```

This will run the default RR environment. It will also assume many default values.

### Defaults

#### Environment

- latest Reproducible Research Environment

#### SSH Key Location

OSX + Linux:

- ~/.ssh/

Windows:

- C:\Users\\<username\>\\.ssh\

#### Mode 

- d: detached 

#### Ports

RStudio

- 8787

SSH

- 2222

If you are already using these ports, Locker will help you reassign them. 