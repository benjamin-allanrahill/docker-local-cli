"""
eval.py
@description: Utility functions for Local Docker CLI
@author: Benjamin Allan-Rahill

"""
import subprocess, shlex, sys
from colors import color


def evalOrDie(cmd, msg="ERROR:", ignore=False):
'''
        evalOrDie(cmd, msg="ERROR:", ignore=False)

        Wrapper func for subprocess.call(). Print specified error message.    
            
        Parameters
        ----------
        cmd: str
            shell command to call
        msg: str
            error msg to show if the command does not complete
        ignore: bool
            wether to ignore a return code of zero as failure   

        Returns
        -------
        str, int
            the STDOUT of the cmd and the return code  
''' 
    cmd = shlex.split(cmd)
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    stdout, stderr = proc.communicate()

    if proc.returncode != 0 and not ignore:
        print(color(msg, fg="yellow"))
        err_str = "COMMAND:\t {} \n\texited with exit value\t {} \n\twith output:\t {} \n\tand error:\t {}".format(
            cmd, proc.returncode, stdout, stderr)
        #raise Exception(err_str)
        sys.exit()

    return stdout.decode('utf-8'), proc.returncode


def callWithPipe(cmd, msg="ERROR:", ignore=False):
    '''
        callWithPipe(cmd, msg="ERROR:", ignore=False)

        Wrapper func for subprocess.call() for calling with a single pipe. Print specified error message.    
            
        Parameters
        ----------
        cmd: str
            shell command to call
        msg: str
            error msg to show if the command does not complete
        ignore: bool
            wether to ignore a return code of zero as failure   

        Returns
        -------
        str, int
            the STDOUT of the cmd and the return code of the second process 
''' 
    # print(cmd)
    cmd1 = shlex.split(cmd.split('|')[0])
    cmd2 = shlex.split(cmd.split('|')[1])
    process_1 = subprocess.Popen(cmd1, stdout=subprocess.PIPE, shell=False)
    process_2 = subprocess.Popen(cmd2,
                                 stdin=process_1.stdout,
                                 stdout=subprocess.PIPE,
                                 shell=False)
    # Allow process_1 to receive a SIGPIPE if process_wc exits.
    process_1.stdout.close()
    if process_2.returncode != 0 and not ignore:
        print(color(msg, fg="yellow"))
        err_str = "COMMAND:\t {} \n\texited with exit value\t {} \n\twith output:\t {} \n\tand error:\t {}".format(
            cmd, process_2.returncode, process_2.stdout, process_2.stderr)
        raise Exception(err_str)

    stdout, stderr = process_2.communicate()
    return stdout.decode('utf-8'), process_2.returncode


# See here https://gist.github.com/garrettdreyfus/8153571
def yes_or_no(question):
    '''
        yes_or_no(question)

        Get yes or no input from the user    
            
        Parameters
        ----------
        question: str
            yes or no question to ask the user
        Returns
        -------
        bool
            if they answered yes or not  
''' 
    reply = str(input(question + ' (y/n): ')).lower().strip()
    if reply[:1] == 'y':
        return True
    if reply[:1] == 'n':
        return False
    else:
        return yes_or_no("Uhhhh... please enter ")