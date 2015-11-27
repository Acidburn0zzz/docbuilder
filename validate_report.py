#!/usr/bin/env python

"""
Cross-checks findings, validates XML files and report files.

Copyright (C) 2015 Peter Mosmans [Go Forward]
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

"""

from __future__ import absolute_import
from __future__ import print_function

import mmap
import re
import subprocess
import xml.etree.ElementTree
import xml.sax


# When set to True, the report will be validated using docbuilder
DOCBUILDER = False
# Snippets may contain XML fragments without the proper entities
SNIPPETDIR = '/snippets/'
REPORT = 'Report/source/report.xml'


if DOCBUILDER:
    import docbuilder_proxy
    import proxy_vagrant


def all_files():
    """
    Returns a list of all files contained in the git repository.
    """
    cmd = ['git', 'ls-files']
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    return process.stdout.read().splitlines()


def validate_files(filenames):
    """
    Checks file extensions and calls appropriate validator function.
    Returns True if all files validated succesfully.
    """
    result = True
    for filename in filenames:
        if (filename.lower().endswith('.xml') or
                filename.lower().endswith('xml"')):
            if SNIPPETDIR not in filename:
                result = validate_xml(filename) and result
    return result


def validate_report():
    """
    Validates XML report file by trying to build it.
    Returns True if the report was built successful.
    """
    host, command = docbuilder_proxy.read_config()
    command = command + ' -c'
    return proxy_vagrant.execute_command(host, command)


def validate_xml(filename):
    """
    Validates XML file by trying to parse it.
    Returns True if the file validated successfully.
    """
    result = True
    print("[+] validating XML file: {0}".format(filename))
    try:
        with open(filename, 'rb') as xml_file:
            xml.sax.parse(xml_file, xml.sax.ContentHandler())
    except xml.sax.SAXException as exception:
        print('[-] validating {0} failed ({1})'.format(filename, exception))
        result = False
    except IOError as exception:
        print('[-] validating {0} failed ({1})'.format(filename, exception))
        result = False
    return result


def get_type(type_path):
    """
    Returns a list of XML filenames based on the type_path.
    """
    return [filename for filename in all_files() if (
        filename.lower().endswith('.xml') and
        re.search('^{0}'.format(type_path), filename))]


def report_string(report_file):
    """
    Return the report_file into a big memory mapped string.
    """
    report = open(report_file)
    return mmap.mmap(report.fileno(), 0, access=mmap.ACCESS_READ)


def cross_check_files(report_text):
    """
    Checks whether all (non) findings are included in the report file.
    Returns True if the checks were successful.
    """
    result = True
    for type_path in ['Findings', 'Non-Findings']:
        for item in get_type(type_path):
            if report_text.find(item) == -1:
                result = False
                print('[-] could not find a reference to {0}'.format(item))
    return result


def find_keyword(xmltree, keyword):
    """
    Finds keywords in an XML tree.
    This function needs lots of TLC.
    """
    result = True
    for tag in xmltree.iter():
        if tag.text:
            if keyword in tag.text:
                print('[-] Found keyword {0} in {1}'.format(keyword, tag))
                result = False
    return result


def main():
    """
    The main program. Cross-checks, validates XML files and report.
    Returns True if the checks were successful.
    """
    result = True
    report_text = report_string(REPORT)
    xmltree = xml.etree.ElementTree.fromstring(report_text)
    if not find_keyword(xmltree, 'TODO'):
        print('[-] Keyword checks failed')
        result = False
    print('[*] Performing cross check on findings and non findings...')
    if not cross_check_files(report_text):
        print('[-] Cross checks failed')
        result = False
    else:
        print('[+] Cross checks successful')
    print('[*] Validating all XML files...')
    if validate_files(all_files()):
        print('[+] Validation checks successful')
        if DOCBUILDER:
            print('[*] Validating report build...')
            result = validate_report() and result
    else:
        print('[-] Validation of XML files failed')
    if result:
        print('[+] Succesfully validated everything. Good to go')
    else:
        print('[-] Errors occurred')


if __name__ == "__main__":
    main()
