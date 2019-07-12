class Container(object):
    from eval import evalOrDie, yes_or_no

    # instance vars 
    image = ''
    cid = ''

    def __init__(self, image):
        self.image = image
    
    # methods
    def startContainer(self):
        docker_start_container = (
                                "docker run " 
                                    "--cap-add=SYS_ADMIN " 
                                    "--device=/dev/fuse " 
                                    "--security-opt=apparmor:unconfined "
                                    "--cap-add=DAC_READ_SEARCH "
                                    "-d -p 2222:22 -p 8787:8787 "
                                    f"{self.image}"
        )
        #print(docker_start_container)
        self.cid = self.evalOrDie(docker_start_container, "There was an error starting the container")
    
    def execute(self, cmd, flags):
        docker_exec_cmd = (
                            "docker exec "
                            f"{flags}"
                            f"{cmd}"
                            f"{self.cid}"
        )
        self.evalOrDie(docker_exec_cmd)

    def cp(self, file_path, dest):
        docker_cp_cmd = (
                        "docker cp "
                        f"{file_path}"
                        f"{dest}"
        )
        self.evalOrDie(docker_cp_cmd)

    def isRunning(self):
        docker_ps_cmd = f"docker ps | grep '^{self.cid[:3]}"
        res, code = self.evalOrDie(docker_ps_cmd, ignore=True)
        
        return True if res != '' and code == 0 else False
        
    def stop(self):
        print("Gracefully stopping the container...")
        docker_stop_cmd = f"docker stop {self.cid}"
        self.evalOrDie(docker_stop_cmd, "There was an error stopping the container")    

    def remove(self):
        
        #check if it is running
        if self.isRunning():
            print("WARNING: The container is running.")
            yes = self.yes_or_no("Would you like to stop the container? (y/n)")
            if yes:
                self.stop()
                print("The container has been gracefully stopped.")
                y = self.yes_or_no("Would you now like to remove the container?")
                if y:
                    self.remove()
                else:
                    pass
            else:
                pass
        else:
            docker_rm_command = f"docker rm {self.cid}"