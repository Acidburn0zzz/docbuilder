#!/usr/bin/env python

"""
Builds PDF files from (intermediate fo and) XML files.

Copyright (C) 2015 Peter Mosmans [Go Forward]
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

from __future__ import absolute_import
from __future__ import print_function
import argparse
import os
import subprocess
from subprocess import PIPE
import sys
import textwrap


# The magic tag which gets replaced by the git short commit hash
GITREV = 'GITREV'


def parse_arguments():
    """
    Parses command line arguments.
    """
    global verboseprint
    global verboseerror
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''\
Builds PDF files from (intermediate fo and) XML files.

Copyright (C) 2015 Peter Mosmans [Go Forward]
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.'''))
    parser.add_argument('-c', '--clobber', action='store_true',
                        help='overwrite output file if it already exists')
    parser.add_argument('--fop-config', action='store',
                        default='/usr/local/bin/fop-1.1/conf/rosfop.xconf',
                        help='fop configuration file (default /usr/local/bin/fop-1.1/conf/rosfop.xconf')
    parser.add_argument('-f', '--fop', action='store', default='./Report/target/report.fo',
                        help='intermediate fop output file (default: ./Report/target/report.fo)')
    parser.add_argument('-i', '--input', action='store', default='./Report/source/report.xml',
                        help='input file (default: ./Report/source/report.xml)')
    parser.add_argument('-x', '--xslt', action='store', default='./Report/xslt/content.xsl',
                        help='input file (default: ./Report/xslt/auto.xsl)')
    parser.add_argument('-o', '--output', action='store', default='./Report/target/latest.pdf',
                        help='output file name (default: ./Report/target/latest.pdf')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='increase output verbosity')
    parser.add_argument('-w', '--warnings', action='store_true',
                        help='show warnings')
    args = parser.parse_args()
    if args.verbose: #pylint: disable=missing-docstring
        def verboseprint(*args):
            for arg in args:
                print(arg, end="")
            print()
        def verboseerror(*args):
            for arg in args:
                print(arg, end="", file=sys.stderr)
            print(file=sys.stderr)
    else:
        verboseprint = lambda *a: None
        verboseerror = lambda *a: None
    return args.input, args.xslt, args.fop, args.output, args.fop_config, args.clobber


def print_output(stdout, stderr):
    """
    Prints out standard out and standard err using the verboseprint function.
    """
    if stdout:
        verboseprint('[+] stdout: {0}'.format(stdout))
    if stderr:
        verboseerror('[-] stderr: {0}'.format(stderr))


def change_tag(fop):
    """
    Replaces GITREV in document by git commit shorttag.
    """
    cmd = ['git', 'log', '--pretty=format:%h', '-n', '1']
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    shorttag, _stderr = process.communicate()
    if not process.returncode:
        fop_file = open(fop).read()
        if GITREV in fop_file:
            fop_file = fop_file.replace(GITREV, shorttag)
            with open(fop, 'w') as new_file:
                new_file.write(fop_file)
            print('[+] Embedding git version information into document')


def to_fo(binary, input_file, xsl_file, fop):
    """
    Creates a fo output file based on a XML file.
    """
    cmd = ['java', '-jar', binary, '-s:' + input_file,
           '-xsl:' + xsl_file, '-o:' + fop, '-xi']
    process = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    print_output(stdout, stderr)
    if process.returncode:
        print_exit('[-] Error creating fo file from XML input',
                   process.returncode)
    else:
        change_tag(fop)
    return True


def to_PDF(binary, config, fop, output_file):
    """
    Creates a PDF file based on a fo file.
    """
    cmd = [binary, '-c', config, fop, output_file]
    try:
        process = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        result = process.returncode
        print_output(stdout, stderr)
    except OSError as exception:
        print_exit('[-] ERR: {0}'.format(exception.strerror), exception.errno)
    return result


def print_exit(text, result):
    """
    Prints error message and exits with result code.
    """
    print(text, file=sys.stderr)
    sys.exit(result)


def main():
    """
    The main program.
    """
    global verboseerror
    global verboseprint
    result = -1
    fop_binary = '/usr/local/bin/fop-1.1/fop'
    saxon_binary = '/usr/local/bin/saxon/saxon9he.jar'
    input_file, xsl_file, fop_output, output_file, fop_config, clobber = parse_arguments()
    if not os.path.isfile(input_file):
        print_exit('[-] Cannot find input file {0}'.format(input_file), result)
    try:
        if os.path.isfile(output_file):
            if not clobber:
                print_exit('[-] Output file {0} already exists. '.
                           format(output_file) +
                           'Use -c (clobber) to overwrite',
                           result)
            os.remove(output_file)
            verboseprint('[+] Overwriting {0}'.format(output_file))
    except OSError as exception:
        print_exit('[-] Could not remove/overwrite file {0} ({1})'.
                   format(output_file, exception.strerror), result)
    result = (to_fo(saxon_binary, input_file, xsl_file, fop_output) and
              to_PDF(fop_binary, fop_config, fop_output, output_file))
    if result == 0:
        print('[+] Succesfully build, output at {0}'.format(output_file))
    else:
        print_exit('[-] Unsuccessful (error {0})'.format(result), result)


if __name__ == "__main__":
    main()
