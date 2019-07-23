# files.py

from locker.utils import cpFrom, cpTo

def add(source, dest, container):
    print(f"Copying file {source} to {dest} in the container {container.id}")
    cpTo(container, source, dest)
    

def grab(source, dest, container):
    print(f"Copying file {source} in the container {container.id} to {dest}")
    cpFrom(container, source, dest)