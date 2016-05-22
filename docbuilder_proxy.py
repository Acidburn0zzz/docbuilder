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
import sys

import proxy_vagrant


CONFIG_FILE = 'docbuilder.yml'




def preflight_checks(rerun=False):
    """
    Checks if all tools are there.
    Exits with 0 if everything went okilydokily
    """
    #pylint: disable=unused-variable
    hostname = 'docbuilder'
    if not rerun:
        print('[*] Checking Vagrant... ', end='')
        if proxy_vagrant.command_fails(['vagrant', 'version']):
            print_error('[-] Could not execute Vagrant', -1)
        print('[*] Checking VirtualBox... ', end='')
        if proxy_vagrant.command_fails(['vboxmanage', '--version']):
            print_error('[-] Could not start VirtualBox', -5)
    sys.stdout.flush()
    if proxy_vagrant.connect_vagrant(hostname):
        print_error('[-] Could not start Vagrant box {0}'.format(hostname), -5)
    print('[*] Checking SSH configuration file... ', end='')
    if proxy_vagrant.execute_command(hostname, 'id', True):
        print_error('[-] Could not execute commands on box {0}'.format(hostname), -5)
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
""YUMMMP"  "YmmMMMM""MMM""""YUMMMMMMMP"`   """"YUMMMMMMM   "W"v 0.4 [PGCM]''')
    sys.exit(0)



def print_error(text, result=False):
    """
    Prints error message.
    When @result, exits with result.
    """
    if len(text):
        print_line('[-] ' + text, True)
    if result:
        sys.exit(result)


def print_line(text, error=False):
    """
    Prints text, and flushes stdout and stdin.
    When @error, prints text to stderr instead of stdout.
    """
    if not error:
        print(text)
    else:
        print(text, file=sys.stderr)
    sys.stdout.flush()
    sys.stderr.flush()


def print_status(text, options=False):
    """
    Prints status message if options array is given and contains 'verbose'.
    """
    if options and options['verbose']:
        print_line('[*] ' + str(text))


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
        print_error('[-] Could not open configuration file {0}: {1}'.
                    format(filename, exception.strerror))
    except IndexError as exception:
        print_error('[-] Missing variables in {0}'.format(filename), -1)
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
        print_error('[-] Could not open file: {0}'.
                    format(exception.strerror), exception.errno)


if __name__ == "__main__":
    main()
