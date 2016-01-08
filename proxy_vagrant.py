#!/usr/bin/env python

"""
Proxies commands 'quickly' to Vagrant using Vagrant's ssh config

Copyright (C) 2015 Peter Mosmans [Go Forward]
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


def vagrant_start(vagrant_id):
    """
    Starts a Vagrant box.
    """
    # pylint: disable=unused-variable
    cmd = ['vagrant', 'up', vagrant_id]
    try:
        print('[+] Starting up machine')
        process = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE)
        _stdout, stderr = process.communicate()
        result = process.returncode
        if result:
            print_exit('[-] Could not start Vagrant machine ({0})'.
                       format(stderr), result)
    except OSError as exception:
        print_exit('[-] Could not find vagrant executable: {0}'.
                   format(exception.strerror), exception.errno)
    return result


def vagrant_connection(hostname, filename):
    """
    Obtains a ssh configuration file from the global Vagrant store.
    """
    # pylint: disable=unused-variable
    if os.path.isfile(filename):
        return True
    result = False
    try:
        vagrant_id, status = vagrant_status(hostname)
        print('[*] Vagrant status of {0} is {1}'.format(hostname, status))
        if status in ('aborted', 'poweroff'):
            vagrant_start(vagrant_id)
            vagrant_id, status = vagrant_status(hostname)
        if status in 'running':
            cmd = ['vagrant', 'ssh-config', vagrant_id]
            process = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE)
            stdout, _stderr = process.communicate()
            if not process.returncode:
                with open(filename, 'w') as config_file:
                    config_file.write(stdout)
                result = 1
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
    print(text, file=sys.stderr)
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
