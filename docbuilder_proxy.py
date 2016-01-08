#!/usr/bin/env python

"""
Executes docbuilder.py on remote ssh machine.

Copyright (C) 2015 Peter Mosmans [Go Forward]
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

from __future__ import absolute_import
from __future__ import print_function

import re
import subprocess
import sys

import proxy_vagrant


CONFIG_FILE = 'docbuilder.yml'


def print_exit(text, result):
    """
    Prints error message and exits with result code.
    """
    print(text, file=sys.stderr)
    sys.exit(result)


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
        print(stdout, stderr)
    else:
        print('OK')
    return result


def preflight_checks(rerun=False):
    """
    Checks if all tools are there.
    Exits with 0 if everything went okilydokily
    """
    #pylint: disable=unused-variable
    if not rerun:
        print('[*] Checking Vagrant... ', end='')
        if command_fails(['vagrant', 'version']):
            print_exit('[-] Could not execute Vagrant', -1)
        print('[*] Checking VirtualBox... ', end='')
        if command_fails(['vboxmanage', '--version']):
            print_exit('[-] Could not start VirtualBox', -5)
    print('[*] Checking whether docbuilder is started... ', end='')
    sys.stdout.flush()
    vagrant_id, status = proxy_vagrant.vagrant_status('docbuilder')
    print(status)
    if status not in 'running':
        print('[*] Trying to start Vagrant box... ', end='')
        if command_fails(['vagrant', 'up', vagrant_id]):
            print_exit('[-] Could not start Vagrant box', -5)
    print('[*] Trying to connect to Vagrant box... ', end='')
    sys.stdout.flush()
    result = command_fails(['vagrant', 'ssh', vagrant_id, '-c', 'id'])
    if result:
        if rerun:
            print_exit('[-] Failed', -6)
        print('[*] Vagrant status could have been incorrect... rechecking')
        preflight_checks(True)
    print('[*] Trying to read local configuration... ', end='')
    _host, _command = read_config(CONFIG_FILE)
    print ('OK')
    print('[+] All checks successful. Ready to rock.')
    print(r'''
     ::::::..
      ;;; ``;;
       [[[,/[['
        $$$$$$c
         888  "88,
:::::::-. MMM ... "W"   .,-:::::
 ;;,   `';, .;;;;;;;.  ,;;;'````'
 `[[     [[,[[     \[[,[[[
  $$,    $$$$$,     $$$$$$
  888_,o8P'"888,_ _,88P`88bo,__,o,
  MMMMP"`    "YMMMMMP"   "YUMMMMMP"
                .::::::.
                 ;;;`    `
                  '[==/[[\,
                           $
                   88b    dP
                     "YMmMY"
:::::::.   ...    :::::: :::   :::::::-.  .,:::::: :::::::..
 ;;;'';;'  ;;     ;;;;;; ;;;    ;;,   `';,;;;;'' ' ;;;;``;;;;
 [[[__[[\.[['     [[[[[[ [[[   `[[     [[ [[cccc   [[[,/[[['
 $$""""Y$$$$      $$$$$$ $$'    $$,    $$ $$"\"""   $$$$$$c
_88o,,od8P88    .d888888o88oo,._888_,o8P' 888oo,__ 888b "88bo,
""YUMMMP"  "YmmMMMM""MMM""""YUMMMMMMMP"`   """"YUMMMMMMM   "W"v 0.1.1 [PGCM]''')
    sys.exit(0)


def read_config(filename):
    """
    Reads host and command parameters from configuration file.
    """
    try:
        with open(filename, 'r') as config_file:
            contents = config_file.read()
            host = re.findall(r'{0}:\s?(.*)'.format('host'), contents)[0]
            command = re.findall(r'{0}:\s?(.*)'.format('command'), contents)[0]
    except IOError as exception:
        print_exit('[-] Could not open configuration file {0}: {1}'.
                   format(filename, exception.strerror), exception.errno)
    except IndexError as exception:
        print_exit('[-] Missing variables in {0}'.format(filename), -1)
    return host, command


def main():
    """
    Executes COMMAND on BOX.
    """
    options = sys.argv[1:]
    if len(options) == 1 and 'check' in sys.argv[1]:
        preflight_checks()
    host, command = read_config(CONFIG_FILE)
    if len(options):
        command = '{0} {1}'.format(command, ' '.join(options))
    try:
        sys.exit(proxy_vagrant.execute_command(host, command))
    except OSError as exception:
        print_exit('[-] Could not open file: {0}'.
                   format(exception.strerror), exception.errno)


if __name__ == "__main__":
    main()
