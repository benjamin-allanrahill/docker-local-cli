def dropIn(container, cmd, mode):
    container.execute(cmd, flags=mode)