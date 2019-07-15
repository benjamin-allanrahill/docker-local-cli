# cleanup.py 
def stop(containers, mode):
    for container in containers:
        func[mode](container)
    
def graceful(container):
    container.stop()

def kill(container):
    container.kill()

func = {False: graceful, True: kill }