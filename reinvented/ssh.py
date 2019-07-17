import paramiko

def ssh(host, user, keypath):
    key = paramiko.RSAKey.from_private_key_file(keypath)
    client = paramiko.SSHClient()
    client..set_missing_host_key_policy(paramiko.AutoAddPolicy())

    client.connect(hostname=host, username=user, pkey=key)
