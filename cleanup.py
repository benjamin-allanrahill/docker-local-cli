# cleanup.py

def cleanup(containers, quiet):
    if quiet:
        for c in containers:
            c.stop()
            c.remove()
    else:
        for c in containers:
            print(f"Removing container: {c.cid}")
            c.remove()