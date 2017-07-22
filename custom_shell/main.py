#!/usr/bin/python
import os
import sys
import time
import shlex
import requests
import json

SHELL_STATUS_RUN = 1
SHELL_STATUS_STOP = 0

BASE_URL = 'http://localhost:50070/webhdfs/v1'

PATH_MASK = '{permission}    - {owner:<11} {group} {length:>10} {modtime} {path}'
#-------------------------------------------------------------------------------
# Web exec
#-------------------------------------------------------------------------------
def webexec(tokens):
    parent = tokens[-1]
    print 'parent', parent
    r = requests.get(BASE_URL + '{0}/?op=LISTSTATUS'.format(parent))
    if r.status_code != 200:
        # Handle error
        return

    for entry in r.json()['FileStatuses']['FileStatus']:
        permissions = '-'
        _type = entry['type']
        if _type == 'DIRECTORY':
            permissions = 'd'
        octal = int(entry['permission'],8)
        for i, s in enumerate('rwxrwxrwx'):
            if (1 << (8-i)) & octal:
                permissions += s
            else:
                permissions += '-'

        owner = entry['owner']
        group = entry['group']
        length = entry['length']
        # Time stamp in milliseconds since the Epoch
        ts = int(float(entry['modificationTime']/1000))
        modtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ts))
        suffix = entry['pathSuffix']
        path = os.path.join(parent, suffix)
        print PATH_MASK.format(permission=permissions,
                               owner=owner,
                               group=group,
                               length=length,
                               modtime=modtime,
                               path=path
        )




#-------------------------------------------------------------------------------
# Execution of real processes
#-------------------------------------------------------------------------------
def analyze(tokens):
    if tokens[0] == 'hdfs' and tokens[1] == 'dfs':
        return True
    return False

#-------------------------------------------------------------------------------
# Execution of real processes
#-------------------------------------------------------------------------------
def execute(cmd_tokens):
    # Fork a child process
    pid = os.fork()
    # The child process
    if pid == 0:
        # Replace child process memory with command
        os.execvp(cmd_tokens[0], cmd_tokens)
    # The parent process
    elif pid > 0:
        # Wait until child process is finished
        while True:
            wpid, status = os.waitpid(pid, 0)
            # Child exits normally / terminated by a signal
            if os.WIFEXITED(status) or os.WIFSIGNALED(status):
                break

    return SHELL_STATUS_RUN

#-------------------------------------------------------------------------------
# Loop
#-------------------------------------------------------------------------------
def shell():
  status = SHELL_STATUS_RUN
  while status == SHELL_STATUS_RUN:
    # Display a command prompt
    sys.stdout.write('hdfs> ')
    sys.stdout.flush()
    # Read command input
    cmd = sys.stdin.readline()
    # Tokenize the command input
    cmd_tokens = shlex.split(cmd)
    # Check if this command is casheable
    if not analyze(cmd_tokens):
        continue
    webexec(cmd_tokens)
    # Execute the command and retrieve new status
#    status = execute(cmd_tokens)

#-------------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------------
if __name__ == "__main__":
    # Exit gracefully when ctrl-c
    try:
        shell()
    except KeyboardInterrupt:
        pass
