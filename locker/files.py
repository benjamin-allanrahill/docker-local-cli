# files.py
import os
from locker.utils import cpFrom, cpTo

def add(container, source, dest):
    print(dest)
    print(f"Copying file {source} to {dest} in the container {container.id}")
    pwd = os.getcwd()
    os.chdir(os.path.abspath(os.path.join(source, os.pardir)))
    cpTo(container, source, dest)
    os.chdir(pwd)
    

def grab(container, source, dest):
    print(f"Copying file {source} in the container {container.id} to {dest}")
    pwd = os.getcwd()
    os.chdir(os.path.abspath(os.path.join(dest, os.pardir)))

    cpFrom(container, source, dest)
    os.chdir(pwd)