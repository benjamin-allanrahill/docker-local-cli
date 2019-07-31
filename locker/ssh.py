#!/usr/bin/env python3.6
"""
ssh.py
@description: Functions for Locker ssh subcommand 
@author: Benjamin Allan-Rahill

"""
import paramiko, os, cmd, subprocess
from locker.utils import cpFrom, cpTo, execute
from locker.eval import evalOrDie, yes_or_no
from colors import color


def ssh(dport):
    '''
        ssh(dport)

        ssh into a running container   
            
        Parameters
        ----------
        dport: str
            the port locally that maps to the ssh port in the container
    '''
    ssh_cmd = ['ssh', 'domino@localhost', '-p', f'{dport}']
    evalOrDie(' '.join(ssh_cmd), "There was an error during ssh")


def copyKeys(container, location, user):
    '''
        copyKeys(container, location, user)
        
        copy ssh keys into a running container 
            
        Parameters
        ----------
        container: Container
            the container to copy keys to 
        location: str
            path to the .ssh directory 
        user: str
            the name of the user 

    '''
    if not yes_or_no("Do you have SSH keys to add?"):
        return

    wkdir = os.getcwd()

    # test to see if location exists
    location = input(
        f"I was looking for your ssh keys at {color(location, fg='red')}. Where should I look? "
    ).strip()

    while not os.path.exists(location):
        print("That path doesn't exist. ")
        location = input("Please enter a valid path: ")

    #change wkdir do that keys can be copied
    os.chdir(os.path.abspath(location))

    cpTo(container, f"id_rsa", f"/home/domino/.ssh/id_rsa_{user}")
    cpTo(container, f"id_rsa.pub", f"/home/domino/.ssh/id_rsa_{user}.pub")

    # append public key to authorized keys
    execute(
        container,
        f" sh -c 'cat /home/domino/.ssh/id_rsa_{user}.pub >> /home/domino/.ssh/authorized_keys'"
    )

    execute(container, "chmod 700 /home/domino/.ssh")
    execute(container, f"chmod 600 /home/domino/.ssh/id_rsa_{user}")
    execute(container, f"chmod 644 /home/domino/.ssh/id_rsa_{user}.pub")

    os.chdir(wkdir)


def sshExec(cmd, sport):
    '''
        sshExec(cmd, sport)

        run a command detached through ssh        
            
        Parameters
        ----------
        cmd: str
            the shell command to run through ssh 
        sport: str
            the port locally that maps to the ssh port in the container

    '''

    client = paramiko.SSHClient()

    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    print(f"connecting...")
    client.connect(hostname='localhost',
                   port=sport,
                   username='domino',
                   password='domino')
    print("connected")

    print(f"Running {color(cmd, fg='yellow')}")
    stdin, stdout, stderr = client.exec_command(cmd)
    print(stdout)
    print('Executed command')
