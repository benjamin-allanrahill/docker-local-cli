import paramiko, os, cmd, subprocess
from locker.utils import cpFrom, cpTo, execute
from colors import color

def ssh(dport):
    ssh_cmd = ['echo', 'domino', '|', 'ssh', 'domino@localhost', '-p', f'{dport}']
    subprocess.call(' '.join(ssh_cmd), shell=True)
    try:
        subprocess.call(' '.join(ssh_cmd), shell=True)
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

    print(f"connecting...")
    client.connect(hostname='localhost', port=sport, username='domino', password='domino')
    print("connected")

    print(f"Running {color(cmd, fg='yellow')}")
    stdin, stdout, stderr = client.exec_command(cmd)
    print(stdout)
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