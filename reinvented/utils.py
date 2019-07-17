import pexpect
from pexpect.popen_spawn import PopenSpawn
from eval import evalOrDie
def cpTo(container, file_path, dest):
    docker_cp_cmd = (
                    "docker cp "
                    f"{file_path} "
                    f"{container.id[:3]}:{dest}"
    )
    evalOrDie(docker_cp_cmd)

def cpFrom(container, file_path, dest):
    docker_cp_cmd = (
                    "docker cp "
                    f"{container.id[:3]}:{file_path} "
                    f"{dest}"
    )
    evalOrDie(docker_cp_cmd)

def execute(container, cmd, flags=''):
    docker_exec_cmd = (
                        "docker exec "
                        f"-{flags} "
                        f"{container.id[:3]} "
                        f"{cmd}"
    )
    child = PopenSpawn(docker_exec_cmd)
    


