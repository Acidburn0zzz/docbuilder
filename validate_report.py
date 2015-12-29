#!/usr/bin/env python

"""
Cross-checks findings, validates XML files, offerte and report files.

Copyright (C) 2015 Peter Mosmans [Go Forward]
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

"""

from __future__ import absolute_import
from __future__ import print_function

import mmap
import os
import re
import subprocess
import sys
import xml.sax
from lxml import etree as ElementTree


# When set to True, the report will be automatically fixed
AUTO_FIX = False
# When set to True, the report will be validated using docbuilder
DOCBUILDER = False
# When set to True, incorrect files will be opened by the system (editor)
OPEN_FILES = False
# When set to True, the spelling will be checked
SPELLING = False
VOCABULARY = 'project-vocabulary.pws'
# Snippets may contain XML fragments without the proper entities
SNIPPETDIR = '/snippets/'
OFFERTE = '/offerte.xml'
REPORT = '/report.xml'
# show a warning when line is longer than WARN_LINE
WARN_LINE = 127
# Maximum line length for lines inside <pre> tags
MAX_LINE = 127


if DOCBUILDER:
    import docbuilder_proxy
    import proxy_vagrant
if SPELLING:
    import aspell


def validate_spelling(tree, learn=True):
    """
    Checks spelling of text within tags.
    """
    result = True
    try:
        speller = aspell.Speller(('lang', 'en'),
                                 ('personal-dir', '.'),
                                 ('personal', VOCABULARY))
        root = tree.getroot()
        for section in root.iter():
            if section.text and isinstance(section.tag, basestring) and section.tag not in ('a', 'monospace', 'pre'):
                for word in re.findall('([a-zA-Z]+\'?[a-zA-Z]+)', section.text):
                    if not speller.check(word):
                        if learn:
                            speller.addtoPersonal(word)
                        else:
                            result = False
                            print('[-] misspelled {0}'.format(word.encode('utf-8')))
        if learn:
            speller.saveAllwords()
    except aspell.AspellSpellerError as exception:
        print('[-] Spelling disabled ({0})'.format(exception))
    return result


def all_files():
    """
    Returns a list of all files contained in the git repository.
    """
    cmd = ['git', 'ls-files']
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    return process.stdout.read().splitlines()


def open_editor(filename):
    if sys.platform in ('linux', 'linux2'):
        editor = os.getenv('EDITOR')
        if editor:
            print('{0} {1}'.format(editor, filename))
            sys.stdout.flush()
            subprocess.call([editor, '"{0}"'.format(filename)], shell=True)
        else:
            subprocess.call('xdg-open', filename)
    elif sys.platform == "darwin":
        subprocess.call(['open', filename])
    elif sys.platform == "win32":
        os.system('"{0}"'.format(filename.replace('/', os.path.sep)))


def validate_files(filenames, check_spelling=False, learn=True):
    """
    Checks file extensions and calls appropriate validator function.
    Returns True if all files validated succesfully.
    """
    result = True
    master = ''
    externals = []
    for filename in filenames:
        if (filename.lower().endswith('.xml') or
                filename.lower().endswith('xml"')):
            if True:
#            if SNIPPETDIR not in filename:
                if OFFERTE in filename or REPORT in filename:
                    master = filename
                # try:
                type_result, xml_type = validate_xml(filename, check_spelling, learn, AUTO_FIX)
                result = result and type_result
                if xml_type in ('scan', 'finding', 'non-finding'):
                    externals.append(filename)
#                except:
#                    result = False
    if len(master):
        result = validate_master(master, externals) and result
    return result


def validate_report():
    """
    Validates XML report file by trying to build it.
    Returns True if the report was built successful.
    """
    host, command = docbuilder_proxy.read_config(docbuilder_proxy.CONFIG_FILE)
    command = command + ' -c'
    return proxy_vagrant.execute_command(host, command)


def validate_xml(filename, check_spelling=False, learn=True, auto_fix=AUTO_FIX):
    """
    Validates XML file by trying to parse it.
    Returns True if the file validated successfully.
    """
    result = True
    xml_type = ''
    print("[+] validating XML file: {0}".format(filename))
    try:
        with open(filename, 'rb') as xml_file:
            xml.sax.parse(xml_file, xml.sax.ContentHandler())
        tree = ElementTree.parse(filename, ElementTree.XMLParser(strip_cdata=False))
        type_result, xml_type = validate_type(tree, filename, check_spelling, learn, auto_fix)
        result = validate_long_lines(tree) and result and type_result
        if OPEN_FILES and not result:
            open_editor(filename)
    except (xml.sax.SAXException, ElementTree.ParseError) as exception:
        print('[-] validating {0} failed ({1})'.format(filename, exception))
        result = False
    except IOError as exception:
        print('[-] validating {0} failed ({1})'.format(filename, exception))
        result = False
    return result, xml_type


def get_all_text(node):
    """
    Retrieves all text within tags.
    """
    text_string = node.text or ''
    for element in node:
        text_string += get_all_text(element)
    if node.tail:
        text_string += node.tail
    return text_string.strip()


def is_capitalized(string):
    """
    Checks whether all words start with a capital.
    Returns True if that's the case.
    """
    return string.strip() == capitalize(string)


def capitalize(string):
    """
    Capitalizes each letter
    """
    return' '.join(word[0].upper() + word[1:] for word in string.strip().split())


def validate_type(tree, filename, check_spelling, learn, auto_fix):
    """
    Performs specific checks based on type.
    Currently only Finding and Non-Finding are supported.
    """
    result = True
    fix = False
    root = tree.getroot()
    xml_type = root.tag
    attributes = []
    tags = []
    if xml_type == 'pentest_report':
        attributes = ['findingCode']
    if xml_type == 'finding':
        attributes = ['threatLevel', 'type', 'id']
        tags = ['title', 'description', 'technicaldescription', 'impact', 'recommendation']
    if xml_type == 'non-finding':
        attributes = ['id']
        tags = ['title']
    if not len(attributes):
        return result, xml_type
    if check_spelling:
        result = validate_spelling(tree, learn)
    for attribute in attributes:
        if attribute not in root.attrib:
            print('[-] Missing obligatory attribute: {0}'.format(attribute))
            if attribute == 'id':
                root.set(attribute, filename)
                fix = True
            else:
                result = False
        else:
            if attribute == 'threatLevel' and root.attrib[attribute] not in ('Low', 'Moderate', 'Elevated', 'High', 'Extreme'):
                print('[-] threatLevel is not Low, Moderate, High, Elevated or Extreme: {0}'.format(root.attrib[attribute]))
                result = False
            if attribute == 'type' and not is_capitalized(root.attrib[attribute]):
                print('[-] Type missing capitalization: {0}'.format(root.attrib[attribute]))
                root.attrib[attribute] = capitalize(root.attrib[attribute])
                fix = True
    for tag in tags:
        if root.find(tag) is None:
            print('[-] Missing tag: {0}'.format(tag))
            result = False
            continue
        if not get_all_text(root.find(tag)):
            print('[-] Empty tag: {0}'.format(tag))
            result = False
            continue
        if tag == 'title' and not is_capitalized(root.find(tag).text):
            print('[-] Title missing capitalization: {0}'.format(root.find(tag).text))
            root.find(tag).text = capitalize(root.find(tag).text)
            result = False
        if tag == 'description' and get_all_text(root.find(tag)).strip()[-1] != '.':
            print('[*] Description missing final dot: {0}'.format(get_all_text(root.find(tag))))
            root.find(tag).text = get_all_text(root.find(tag)).strip() + '.'
            fix = True
    if auto_fix and fix:
        print('[+] Automatically fixed')
        tree.write(filename)
    return (result and not fix), xml_type


def validate_long_lines(tree):
    """
    Checks whether <pre> section contains lines longer than MAX_LINE characters
    Returns True if the file validated successfully.
    """
    result = True
    root = tree.getroot()
    for pre_section in root.iter('pre'):
        if pre_section.text:
            for line in pre_section.text.splitlines():
                if len(line.strip()) > WARN_LINE:
                    if len(line.strip()) > MAX_LINE:
                        print('[-] Line inside <pre> too long: {0}'.
                              format(line.encode('utf-8').strip()))
                    else:
                        print('[*] Line inside <pre> long ({0} characters)'.
                              format(len(line.strip())))
                        result = False
    return result


def validate_master(filename, externals):
    """
    Validates master file.
    """
    result = True
    print('[*] Validating master file {0}'.format(filename))
    try:
        xmltree = ElementTree.parse(filename, ElementTree.XMLParser(strip_cdata=False))
        if not find_keyword(xmltree, 'TODO'):
            print('[-] Keyword checks failed')
            result = False
        print('[*] Performing cross check on scans, findings and non findings...')
        if not cross_check_files(report_string(filename), externals):
            print('[-] Cross checks failed')
            result = False
        else:
            print('[+] Cross checks successful')
    except ElementTree.ParseError as exception:
        print('[-] validating {0} failed ({1})'.format(filename, exception))
        result = False
    return result


def report_string(report_file):
    """
    Return the report_file into a big memory mapped string.
    """
    try:
        report = open(report_file)
        return mmap.mmap(report.fileno(), 0, access=mmap.ACCESS_READ)
    except IOError as exception:
        print('[-] Could not open {0} ({1})'.format(report_file, exception))
        sys.exit(-1)


def cross_check_files(report_text, externals):
    """
    Checks whether all (non) findings are included in the report file.
    Returns True if the checks were successful.
    """
    result = True
    for external in externals:
        if report_text.find(external) == -1:
            print('[-] could not find a reference to {0}'.format(external))
            result = False
    return result


def find_keyword(xmltree, keyword):
    """
    Finds keywords in an XML tree.
    This function needs lots of TLC.
    """
    result = True
    for tag in xmltree.iter():
        if tag.tag == 'section':
            section = tag.attrib['id']
        if tag.text:
            if keyword in tag.text:
                print('[-] {0} found in section {1}'.
                      format(keyword, section))
                result = False
    return result


def main():
    """
    The main program. Cross-checks, validates XML files and report.
    Returns True if the checks were successful.
    """
    learn = False
    options = sys.argv[1:]
    if len(options) == 1 and 'learn' in sys.argv[1]:
        print('[+] Adding unknown words to {0}'.format(VOCABULARY))
        learn = True
    if SPELLING:
        if not os.path.exists(VOCABULARY):
            print('[+] Creating project-specific vocabulary file {0}'.
                  format(VOCABULARY))
            learn = True
    print('[*] Validating all XML files...')
    result = validate_files(all_files(), SPELLING, learn)
    if result:
        print('[+] Validation checks successful')
        if DOCBUILDER:
            print('[*] Validating report build...')
            result = validate_report() and result
    if result:
        print('[+] Succesfully validated everything. Good to go')
    else:
        print('[-] Errors occurred')
    if SPELLING and learn:
        print('[*] Don\'t forget to check the vocabulary file {0}'.
              format(VOCABULARY))


if __name__ == "__main__":
    main()
