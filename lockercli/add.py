# add.py

def add(source, dest, container):
    print(f"Copying file {source} to {dest} in the container {container.cid}")
    container.cpTo(source, dest)