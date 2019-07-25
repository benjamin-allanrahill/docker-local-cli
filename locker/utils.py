#!/usr/bin/env python3.6
"""
utils.py
@description: Container functions for Locker commands 
@author: Benjamin Allan-Rahill

"""
from subprocess import call
from locker.eval import evalOrDie


def cpTo(container, file_path, dest):
    docker_cp_cmd = ("docker cp " f"{file_path} " f"{container.id[:3]}:{dest}")
    evalOrDie(docker_cp_cmd)


def cpFrom(container, file_path, dest):
    docker_cp_cmd = ("docker cp " f"{container.id[:3]}:{file_path} " f"{dest}")
    evalOrDie(docker_cp_cmd)


def execute(container, cmd, flags=''):
    # print(f"EXECUTING: {cmd}")
    docker_exec_cmd = ("docker exec "
                       f"-{flags} "
                       f"{container.id[:3]} "
                       f"{cmd}")
    call(docker_exec_cmd)
