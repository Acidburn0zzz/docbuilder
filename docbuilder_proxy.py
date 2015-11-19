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

import sys

import proxy_vagrant
import yaml


CONFIG_FILE = 'docbuilder.yml'


def print_exit(text, result):
    """
    Prints error message and exits with result code.
    """
    print(text, file=sys.stderr)
    sys.exit(result)


def read_config():
    """
    Reads host and command parameters from configuration file.
    """
    try:
        config = yaml.safe_load(open(CONFIG_FILE))
        host = config['host']
        command = config['command']
    except IOError as exception:
        print_exit('[-] Could not open configuration file {0}: {1}'.
                   format(CONFIG_FILE, exception.strerror), exception.errno)
    except KeyError as exception:
        print_exit('[-] Could not find host and/or command variables in {0}'.
                   format(CONFIG_FILE), -1)
    return host, command


def main():
    """
    Executes COMMAND on BOX.
    """
    options = sys.argv[1:]
    host, command = read_config()
    if len(options):
        command = '{0} {1}'.format(command, ' '.join(options))
    try:
        sys.exit(proxy_vagrant.execute_command(host, command))
    except OSError as exception:
        print_exit('[-] Could not open file: {0}'.
                   format(exception.strerror), exception.errno)


if __name__ == "__main__":
    main()
