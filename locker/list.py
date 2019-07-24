from locker.eval import evalOrDie
def ps(all):
    docker_ps_cmd = f"docker ps {' -a ' if all else ''}"
    
    print(evalOrDie(docker_ps_cmd, "There was an error getting the containers")[0])

def listRegistry(registry):
    curl_cmd = f'curl -s -X GET https://{registry}/v2/_catalog'

    data = evalOrDie(curl_cmd, "There was an error getting the images")
    print(data)

    for repo in data["repositories"]:
        tag_cmd = f'curl  -s -X GET https://myregistry:5000/v2/{repo}/tags/list'
        res = evalOrDie(tag_cmd, "There was en error getting the tags")
        tags = [str(tag) for tag in res["tags"]]
        print(repo)
        print(tags)


def listImages():
    image_cmd = 'docker images'
    
    print(evalOrDie(image_cmd)[0])