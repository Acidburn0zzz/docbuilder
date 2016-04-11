#!/usr/bin/env python

"""
Proxies commands 'quickly' to Vagrant using Vagrant's ssh config

Copyright (C) 2015-2016 Peter Mosmans [Go Forward]
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

from __future__ import absolute_import
from __future__ import print_function

import os
import re
import subprocess
from subprocess import PIPE
import sys

STATES = ['poweroff', 'aborted']
ACTIONS = ['up', 'reload']


def command_fails(cmd):
    """
    Executes command.
    Returns True if command failed.
    """
    stdout = ''
    stderr = ''
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        result = process.returncode
    except OSError as exception:
        result = -1
        print('could not execute {0}'.format(cmd))
        print('[-] {0}'.format(exception.strerror), file=sys.stderr)
    if result:
        print('FAILED')
#        print(stdout, stderr)
    else:
        print('OK')
    return result


def connect_vagrant(hostname, rerun=False):
    """
    Checks if vagrant can be started and is accessible.
    Exits with 0 if everything went okilydokily
    """
    print('[*] Querying status of {0}... '.format(hostname), end='')
    sys.stdout.flush()
    result, vagrant_id = start_vagrant(hostname)
    if not result:
        print_exit('[-] Could not start Vagrant box {0}'.format(hostname), -5)
    print('[*] Trying to connect to {0}... '.format(hostname), end='')
    sys.stdout.flush()
    result = command_fails(['vagrant', 'ssh', vagrant_id, '-c', 'id'])
    if result:
        if rerun:
            print_exit('[-] Failed', -6)
        print('[*] Vagrant status could have been incorrect... rechecking')
        connect_vagrant(hostname, True)


def start_vagrant(hostname, action=0):
    """
    Tries really hard to start a Vagrant instance.
    """
    vagrant_id, status = vagrant_status(hostname)
    if not action:
        print(status)
#    if 'running' in status:
#        return True, vagrant_id
    if 'unknown' in status:
        print_exit('Unknown Vagrant box: ' + hostname, -1)
    if status in STATES:
        if action > len(ACTIONS):
            print_exit('out of options', -1)
            return False, ''
        command = ACTIONS[action]
        print('[*] Not giving up, trying to {0} Vagrant box... '.
              format(command), end='')
        sys.stdout.flush()
        if command_fails(['vagrant', command, vagrant_id]):
            start_vagrant(hostname, action + 1)
    return True, vagrant_id


def vagrant_status(hostname):
    """
    Returns global ID and status of hostname.

    Arguments:
    - `hostname`: hostname of Vagrant box
    """
    # pylint: disable=unused-variable
    status = 'unknown'
    vagrant_id = ''
    cmd = ['vagrant', 'global-status']
    try:
        process = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE)
        stdout, _stderr = process.communicate()
        if not process.returncode and stdout:
            line = re.findall(r'([0-9a-f]*)\s+{0}\s+virtualbox\s+(\w+)\s'.
                              format(hostname), stdout)
            if line:
                vagrant_id, status = line[0]
    except OSError as exception:
        print_exit('[-] Could not find vagrant executable: {0}'.
                   format(exception.strerror), exception.errno)
    return vagrant_id, status


def vagrant_connection(hostname, filename):
    """
    Obtains a ssh configuration file from the global Vagrant store.
    """
    # pylint: disable=unused-variable
    if os.path.isfile(filename):
        return True
    result = False
    result, vagrant_id = start_vagrant(hostname)
    if result:
        try:
            cmd = ['vagrant', 'ssh-config', vagrant_id]
            process = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE)
            stdout, _stderr = process.communicate()
            if not process.returncode:
                with open(filename, 'w') as config_file:
                    config_file.write(stdout)
                    result = True
        except OSError as exception:
            print_exit('[-] Could not find vagrant executable: {0}'.
                       format(exception.strerror), exception.errno)
    return result


def execute_ssh(config_file, hostname, command):
    """
    Executes @command on @hostname using the SSH configuration @config_file.
    """
    cmd = ['ssh', '-F', config_file, hostname, command]
    process = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    print_stdoutput(stdout, stderr)
    return process.returncode


def print_exit(text, result):
    """
    Prints error message and exits with result code.
    """
    print('[-] ' + text, file=sys.stderr)
    sys.exit(result)


def print_stdoutput(stdout, stderr):
    """
    Prints out standard out and standard err using the verboseprint function.
    """
    if stdout:
        print(stdout.strip())
        sys.stdout.flush()
    if stderr:
        print_error(stderr.strip())


def print_error(text):
    """
    Prints output to error stream.
    """
    print(text, file=sys.stderr)
    sys.stderr.flush()


def execute_command(hostname, command):
    """
    Executes @command using ssh on Vagrant box @hostname.
    """
    config_file = hostname + '.ssh-config'
    if not vagrant_connection(hostname, config_file):
        print_error('[-] Could not connect to Vagrant instance of {0}'.
                    format(hostname))
    return execute_ssh(config_file, hostname, command)


def main():
    """
    The main program loop.
    """
    if len(sys.argv) < 3:
        print_exit('Usage: proxy_vagrant.py hostname command', -1)
        hostname = sys.argv[1]
        command = sys.argv[2:]
    return execute_command(hostname, command)


if __name__ == "__main__":
    main()
