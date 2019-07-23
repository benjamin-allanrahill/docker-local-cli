# files.py

from ssh import sshExec

def add(source, dest, container):
    print(f"Copying file {source} to {dest} in the container {container.id}")
    sshExec()

def grab(source, dest, container):
    print(f"Copying file {source} in the container {container.id} to {dest}")
