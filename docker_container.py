from eval import evalOrDie, yes_or_no, callWithPipe
import shlex

class Container(object):
    

    # instance vars 
    image = ''
    cid = ''
    r_port = '8787'

    def __init__(self, image, cid='', r_port='8787'):
        self.image = image
        self.cid = cid
        self.r_port = r_port
    
    # methods
    def startContainer(self, mode='d'):
        if self.isImageRunning():
            print("You already have this image running..")
            if yes_or_no("Do you want to use this container? "):
                self.cid = callWithPipe(f"docker ps | awk '$2==\"{self.image}\" {{ print $1}}'", ignore=True)[0]
            else:
                print("Ports are already allocated. You have to change them to start a new container")
            return 
        docker_start_container = (
                                "docker run " 
                                    "--cap-add=SYS_ADMIN " 
                                    "--device=/dev/fuse " 
                                    "--security-opt=apparmor:unconfined "
                                    "--cap-add=DAC_READ_SEARCH "
                                    f"-{mode} -p 2222:22 -p {self.r_port}:8787 "
                                    f"{self.image}"
        )
        #print(docker_start_container)
        self.cid = evalOrDie(docker_start_container, "There was an error starting the container")[0].strip()
        print(f"container ID is {self.cid}")
    
    def execute(self, cmd, flags=''):
        docker_exec_cmd = (
                            "docker exec "
                            f"{flags} "
                            f"{self.cid[:3]} "
                            f"{cmd}"
        )
        print(docker_exec_cmd)
        evalOrDie(docker_exec_cmd)

    def cpTo(self, file_path, dest):
        docker_cp_cmd = (
                        "docker cp "
                        f"{file_path} "
                        f"{self.cid[:3]}:{dest}"
        )
        evalOrDie(docker_cp_cmd)

    def cpFrom(self, file_path, dest):
        docker_cp_cmd = (
                        "docker cp "
                        f"{self.cid[:3]}:{file_path} "
                        f"{dest}"
        )
        evalOrDie(docker_cp_cmd)

    def isImageRunning(self):
        find_img_cmd = f"docker ps | awk '$2==\"{self.image}\" {{f  = 1}}; END {{ exit !f }}'"
        print(find_img_cmd)
        res, code = callWithPipe(find_img_cmd, ignore=True)
        print(res)
        res = shlex.split(res)
        print(res, code)
        return True if code == 0 else False 

    def isRunning(self):
        docker_ps_cmd = f"docker ps | grep '^{self.cid[:3]}'"
        print(str(self.cid)[:3])
        print(docker_ps_cmd)
        res, code = callWithPipe(docker_ps_cmd, ignore=True)
        
        return True if res != '' and code == 0 else False
        
    def stop(self):
        print("Gracefully stopping the container...")
        docker_stop_cmd = f"docker stop {self.cid}"
        evalOrDie(docker_stop_cmd, "There was an error stopping the container")

    def kill(self):
        print("Killing the container...")
        docker_kill_cmd = f"docker kill {self.cid}"
        evalOrDie(docker_kill_cmd, "There was an error killing the container")    

    def remove(self):    
        #check if it is running
        if self.isRunning():
            print("WARNING: The container is running.")
            yes = yes_or_no("Would you like to stop the container? (y/n)")
            if yes:
                self.stop()
                print("The container has been gracefully stopped.")
                y = yes_or_no("Would you now like to remove the container?")
                if y:
                    self.remove()
                else:
                    pass
            else:
                pass
        else:
            docker_rm_command = f"docker rm {self.cid}"