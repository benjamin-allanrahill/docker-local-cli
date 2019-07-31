"""
list.py
@description: functions for Locker subcommand 'list'
@author: Benjamin Allan-Rahill

"""
import json
from locker.eval import evalOrDie


def ps(all):
    '''
        ps(all)

        run "docker ps" cmd to print containers   
            
        Parameters
        ----------
        all: bool
            stopped containers too?
    '''
    docker_ps_cmd = f"docker ps {' -a ' if all else ''}"

    print(
        evalOrDie(docker_ps_cmd,
                  "There was an error getting the containers")[0])


def listRegistry(registry):
    '''
        listRegistry(registry)

        retrieve image and tag data from a registry    
            
        Parameters
        ----------
        registry: str
            the address of the registry
    '''
    curl_cmd = f'curl -s -X GET https://{registry}/v2/_catalog'

    data = json.loads(
        evalOrDie(curl_cmd, "There was an error getting the images. \nPlease make sure you are connected to the network")[0])

    print("\nREPOSITORY \t\t\t\t\t TAGS")
    for repo in data['repositories']:
        tag_cmd = f'curl  -s -X GET https://{registry}/v2/{repo}/tags/list'
        res = json.loads(
            evalOrDie(tag_cmd, "There was en error getting the tags")[0])
        tags = [str(tag) for tag in res['tags']]
        print(f"{repo} \t {tags}")

    print(
        f"\nUse {registry}/<repo>:<tag> as your environment in the `locker run` cmd.\n"
    )
    print(f"EXAMPLE:\n\t`locker run --env {registry}/{repo}:{tags[0]}")


def listImages():
    '''
        listImages()

        print all the images on the machine    
            
    '''
    image_cmd = 'docker images'
    print(evalOrDie(image_cmd)[0])


def searchDockerHub(name, limit='15'):
    '''
        searchDockerHub(name, limit='15')

        print docker search results     
            
        Parameters
        ----------
        name: str
            the name of the image to search for
        limit: str
            number of images to print
    '''
    search_cmd = f'docker search {name} --limit {limit}'
    print(evalOrDie(search_cmd)[0], "Error getting images...\nPlease make sure you are connected to the network")

def findSimilarImages(image):
    '''
        findSimilarImages(image)

        See if there are any similar images by repository

        Parameters: 
        ===========
        image: str
            The name of the original image 

    '''

    grep_cmd = f"docker images | grep {image} | awk '{{print $1; print $2; print $3}}'"

    # have to 'ignore' error codes when using grep so the program doesnt quit when no match is made
    res, code = callWithPipe(
        grep_cmd, "There was an error trying to find similar images, on Windows this only works in Git Bash")

    if res != '' and code == 0:
        info = res.replace('\n', ' ').split()
        print("Found these images under the same repository:")
        print(*(f"\t{info[i*3]}" for i in range(len(info) // 3)))
        
        print("You can run one of these using the --env flag for `locker run`")
    else:
        print("There were no similar images were found locally")
        print("You can use `locker search` or `locker list` to find other images ")
