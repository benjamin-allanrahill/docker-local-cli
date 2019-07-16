from eval import evalOrDie, yes_or_no, callWithPipe
import shlex, random

class Container(object):
    

    # instance vars 
    image = ''
    cid = ''
    ports = {'ssh': '2222', 'r':'8787'}
    created = ''

    def __init__(self, image='', cid='', ports={'22': '2222', '8787':'8787'}, created = ''):
        self.image = image
        self.cid = cid
        self.ports = ports
        self.created = created

    # methods
    def startContainer(self, mode='d'):
        if self.isImageRunning():
            print("You already have this image running..")
        docker_start_container = (
                                "docker run " 
                                    "--cap-add=SYS_ADMIN " 
                                    "--device=/dev/fuse " 
                                    "--security-opt=apparmor:unconfined "
                                    "--cap-add=DAC_READ_SEARCH "
                                    f"-{mode} -p {self.ports['22']}:22 -p {self.ports['8787']}:8787 "
                                    f"{self.image}"
        )
        #print(docker_start_container)
        self.cid = evalOrDie(docker_start_container, "There was an error starting the container")[0].strip()
        print(f"container ID is {self.cid}")
    
    def execute(self, cmd, flags=''):
        docker_exec_cmd = (
                            "exec docker exec "
                            f"-{flags} "
                            f"{self.cid[:3]} "
                            f"{cmd}"
        )
        print(docker_exec_cmd)
        res, code = evalOrDie(docker_exec_cmd)
        #print(res)

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
            evalOrDie(docker_rm_command, "There was an error removing the container")

    def changePortsRand(self, used):
        print(self.ports)
        for cport, lport in self.ports.items():
            print(cport)    
            random_port = str(random.randint(3000, 9000))

            if random_port in used:
                random_port = str(int(random_port) + 1)
            else:
                self.ports[cport] = random_port
                print(f"The new port for {cport}/tcp is: {random_port}")