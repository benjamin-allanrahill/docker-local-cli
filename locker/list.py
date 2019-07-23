from locker.eval import evalOrDie
def ps(all):
    docker_ps_cmd = f"docker ps {' -a ' if all else ''}"
    
    print(evalOrDie(docker_ps_cmd, "There was an error getting the containers")[0])

def listRegistry(registry):
    curl_cmd = f'curl -X GET https://{registy}/v2/_catalog'

    data = evalOrDie(curl_cmd, "There was an error getting the images")
    print(data)

def listImages():
    image_cmd = 'docker images'
    
    print(evalOrDie(image_cmd)[0])