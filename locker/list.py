import json
from locker.eval import evalOrDie
def ps(all):
    docker_ps_cmd = f"docker ps {' -a ' if all else ''}"
    
    print(evalOrDie(docker_ps_cmd, "There was an error getting the containers")[0])

def listRegistry(registry):
    curl_cmd = f'curl -s -X GET https://{registry}/v2/_catalog'

    data = json.loads(evalOrDie(curl_cmd, "There was an error getting the images")[0])
    #print(data)
    #print(type(data))

    print("\nREPOSITORY \t\t\t\t\t TAGS")
    for repo in data['repositories']:
        tag_cmd = f'curl  -s -X GET https://{registry}/v2/{repo}/tags/list'
        res = json.loads(evalOrDie(tag_cmd, "There was en error getting the tags")[0])
        tags = [str(tag) for tag in res['tags']]
        print(f"{repo} \t\t\t\t\t {tags}")

    print(f"\nUse {registry}/<repo>:<tag> as your environment in the `locker run` cmd.\n")
    print(f"EXAMPLE:\n\t`locker run --env {registry}/{repo}:{tags[0]}")

def listImages():
    image_cmd = 'docker images'
    print(evalOrDie(image_cmd)[0])

def searchDockerHub(name, limit='15'):
    search_cmd = f'docker search {name} --limit {limit}'
    print(evalOrDie(search_cmd)[0])