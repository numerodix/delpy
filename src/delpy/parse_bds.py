#!/usr/bin/env python
#
# Copyright: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

if __name__ == '__main__': import __path__

import os
import sys
import xml.dom.minidom

p = os.path.dirname(sys.modules[__name__].__file__)
sys.path.append(os.path.join(p, 'lib'))
from delpy.lib import xpath
from delpy.lib import prettyprinter

# ref: http://www.boddie.org.uk/python/XML_intro.html
# ref: http://py-dom-xpath.googlecode.com/svn/trunk/doc/index.html

def get_keypairs(node_root, path, tagname):
    keypairs = {}
    node_baseline = xpath.findnode('%s/%s' % (path, tagname), node_root)
    if node_baseline:
        nodes_tagname = xpath.find(tagname, node_baseline)

        for node_tag in nodes_tagname:
            keyname = xpath.findvalue('@Name', node_tag)
            keyvalue = None
            if hasattr(node_tag, 'childNodes'):
                values = node_tag.childNodes
                if values:
                    keyvalue = values[0].nodeValue
            keypairs[keyname] = keyvalue
    return keypairs

def parseBdsGroup(s):
    node_root = xml.dom.minidom.parseString(s)
    dct = {}
    elems = ('Projects',)
    for elem in elems:
        dct[elem] = get_keypairs(node_root, 'BorlandProject/Default.Personality', elem)
    return dct

def parseBdsProj(s):
    node_root = xml.dom.minidom.parseString(s)
    dct = {}
    elems = ('Source', 'FileVersion', 'Compiler', 'Linker', 'Directories',
             'Parameters', 'Language', 'VersionInfo', 'VersionInfoKeys')
    for elem in elems:
        dct[elem] = get_keypairs(node_root, 'BorlandProject/Delphi.Personality', elem)
    return dct


if __name__ == '__main__':
    file = sys.argv[1]
    s = open(file).read()
    dct = {}

    _, ext = os.path.splitext(file)
    if ext == '.bdsproj':
        dct = parseBdsProj(s)
    elif ext == '.bdsgroup':
        dct = parseBdsGroup(s)
    prettyprinter.pp(dct)
