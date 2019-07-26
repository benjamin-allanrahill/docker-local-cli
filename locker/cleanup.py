# cleanup.py
def cleanup(containers, quiet):
    if quiet:
        for c in containers:
            c.stop()
            c.remove()
    else:
        if type(containers) != list:
            print(f"Removing container: {containers.id}")
            containers.stop()
            containers.remove()
        else:
            for c in containers:
                print(f"Removing container: {c.id}")
                c.stop()
                c.remove()