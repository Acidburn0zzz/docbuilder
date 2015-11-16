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


def vagrant_connection(hostname, filename):
    """
    Obtains a ssh configuration file from the global Vagrant store.
    """
    if os.path.exists(filename):
        return True
    result = False
    cmd = ['vagrant', 'global-status']
    try:
        process = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE)
        stdout, _stderr = process.communicate()
        if not process.returncode:
            vagrant_id = re.findall(r'([0-9a-f]*)\s+{0}\s+virtualbox\s+running'.
                                    format(hostname), stdout)
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
    if stderr:
        print(stderr.strip(), file=sys.stderr)


def execute_command(hostname, command):
    """
    Executes @command using ssh on Vagrant box @hostname.
    """
    config_file = hostname + '.ssh-config'
    if not vagrant_connection(hostname, config_file):
        print_exit('[-] Could not obtain Vagrant ssh connection details for {0}'.
                   format(hostname), -1)
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
