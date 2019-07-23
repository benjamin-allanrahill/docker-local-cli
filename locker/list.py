from locker.eval import evalOrDie
def ps(all):
    docker_ps_cmd = f"docker ps {' -a ' if all else ''}"
    
    print(evalOrDie(docker_ps_cmd, "There was an error getting the containers")[0])

def listRegistry():
    curl_cmd = 'curl -X GET https://docker.rdcloud.bms.com:443/v2/_catalog'

    data = evalOrDie(curl_cmd, "There was an error getting the images")

def listImages():
    image_cmd = 'docker images'
    
    print(evalOrDie(image_cmd)[0])