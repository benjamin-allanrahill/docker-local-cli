import paramiko, os, cmd, subprocess
from utils import cpFrom, cpTo, execute

def ssh(dport):
    ssh_cmd = ['ssh', 'domino@localhost']

    try:
        subrpocess.call(ssh_cmd)
    except:
        print("There was an error during ssh")
        exit(1)

def copyKeys(container, location, user):

    wkdir = os.getcwd()
    #change wkdir do that keys can be copied
    os.chdir(location)

    cpTo(container, f"id_rsa", f"/home/domino/.ssh/id_rsa_{user}")
    cpTo(container, f"id_rsa.pub", f"/home/domino/.ssh/id_rsa_{user}.pub")
   
    # append public key to authorized keys 
    execute(container, f"cat /home/domino/.ssh/id_rsa_{user}.pub >> /home/domino/.ssh/authorized_keys")

    os.chdir(wkdir)

def sshExec(cmd, sport):
    client = paramiko.SSHClient()
    
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    print(f"connecting to {host}")
    client.connect(hostname='localhost', port=sport, username='domino', password='domino')
    print("connected")

    print(f"Running {cmd}")
    client.exec_command(cmd)
    print('Executed command')


class SshCommand(cmd.Cmd):
    """ Simple shell to run a command on the host """

    prompt = 'locker ssh @localhost >>> '

    def __init__(self, host):
        cmd.Cmd.__init__(self)
        self.host = host

    def do_run(self, command):
        """run 
        Execute this command on all hosts in the list"""
        if command:
            stdin, stdout, stderr = self.host.exec_command(command)
            stdin.close()
            for line in stdout.read().splitlines():
                print( 'host: %s: %s' % (self.host, line))
        else:
            print("usage: run ")