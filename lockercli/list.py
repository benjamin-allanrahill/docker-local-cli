from eval import callWithPipe, evalOrDie
def listRunning():
    cid_cmd = "docker ps -q"
    image_cmd = "docker ps | awk '{print $2}'"
    created_cmd = "docker ps | awk '{print $4}"
    
    cids = evalOrDie(cid_cmd, "There was an error getting container IDs")[0].split()
    images = callWithPipe(image_cmd, "There was an error getting the images")[0].split()
    created = callWithPipe(created_cmd, "There was an error getting the creation data")[0].split()

    # TODO: Write pretty print function 