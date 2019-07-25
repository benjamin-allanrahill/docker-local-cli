"""
files.py
@description: Functions for dealin with add and grab Locker subcommands 
@author: Benjamin Allan-Rahill

"""
import os
from locker.utils import cpFrom, cpTo


def add(container, source, dest):
    '''
        add(container, source, dest)

        copy file/dir to container  

        Parameters
        ----------
        container: Container
            container object to copy to 
        source: str
            path to copy from on the local machine
        dest: str
            path to put the file in the container  
    ''' 

    print(f"Copying file {source} to {dest} in the container {container.id}")
    
    # need to change to same directory to use docker cp 
    pwd = os.getcwd()
    os.chdir(os.path.abspath(os.path.join(source, os.pardir)))
    
    cpTo(container, source, dest)
    
    os.chdir(pwd) # change back


def grab(container, source, dest):
    '''
        grab(container, source, dest)

        copy file/dir from container  

        Parameters
        ----------
        container: Container
            container object to copy to 
        source: str
            path to copy from in the container
        dest: str
            path to put the file on the local machine 
    ''' 

    print(f"Copying file {source} in the container {container.id} to {dest}")
    
    # need to change to same directory to use docker cp 
    pwd = os.getcwd()
    os.chdir(os.path.abspath(os.path.join(dest, os.pardir)))

    cpFrom(container, source, dest)

    os.chdir(pwd) # change back 