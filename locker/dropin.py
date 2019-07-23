from locker.ssh import sshExec, ssh

def dropIn(container, cmd, mode):
    ports = container.ports

    print(ports)
    
    ssh_port = ports['22/tcp'][0]['HostPort']

    print(ssh_port)

    if mode == 'ti':
        ssh(ssh_port)
    else:
        sshExec(cmd, ssh_port)