"""
dropin.py
@description: functions for locker drop-in subcommand
@author: Benjamin Allan-Rahill

"""
from locker.ssh import sshExec, ssh
from locker.utils import execute


def dropIn(container, cmd, mode):
    '''
        dropIn(container, cmd, mode)

        use docker exec to get into a container    

        Parameters
        -------
        container: Container
            the container to exec into
        cmd: str
            the cmd to run if mode == d
        mode: str
            run detached or interactive 
    '''
    execute(container, cmd, mode)


def sshIn(container, cmd, mode):
    '''
        sshIn(container, cmd, mode)

        use ssh to exec into a running container   

        Parameters
        -------
        container: Container
            the container to exec into
        cmd: str
            the cmd to run if mode == d
        mode: str
            run detached or interactive 
    '''
    ports = container.ports

    print(ports)

    ssh_port = ports['22/tcp'][0]['HostPort']

    print(ssh_port)

    if mode == 'ti':
        ssh(ssh_port)
    else:
        sshExec(cmd, ssh_port)