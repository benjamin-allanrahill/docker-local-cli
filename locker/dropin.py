from locker.ssh import sshExec, ssh
from locker.utils import execute

def dropIn(container, cmd, mode):
    execute(container, cmd, mode)

def sshIn(container, cmd, mode):
    ports = container.ports

    print(ports)
    
    ssh_port = ports['22/tcp'][0]['HostPort']

    print(ssh_port)

    if mode == 'ti':
        ssh(ssh_port)
    else:
        sshExec(cmd, ssh_port)