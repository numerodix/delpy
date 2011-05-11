#!/usr/bin/env python
#
# Copyright: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

if __name__ == '__main__': import __path__

from optparse import OptionParser
import re
import sys

from delpy.lib import prettyprinter

from delpy import model
from delpy import parse_bds
from delpy import parse_source
from delpy import util


# Delphi source

def find_unifyNewlines(s, stripcomments=False):
    s = parse_source.unifyNewlines(s)
    return s

def find_stripComments(s, stripcomments=False):
    s = parse_source.transStripComments(s)
    return s

def find_stripCommentsKeepDirectives(s, stripcomments=False):
    s = parse_source.transStripComments(s, keep_directives=True)
    return s

def find_stripCommentsKeepAllDirectives(s, stripcomments=False):
    s = parse_source.transStripComments(s, keep_directives=True,
                                        keep_all_directives=True)
    return s

def find_programHeader(s, stripcomments=False):
    pFileHeader = parse_source.get_pFileHeader()

    if stripcomments:
        s = parse_source.transStripComments(s)

    for item in pFileHeader.scanString(s):
        toks, _, _ = item
        # return, only one instance of a header in a file
        return (toks[0], toks[1])

def findAbstractImports(s, parser, stripcomments=False):
    if stripcomments:
        s = parse_source.transStripComments(s)

    units = []
    for item in parser.scanString(s):
        toks, _, _ = item
        for unititem in toks:
            name, filename = None, None
            try:
                name = unititem[0]
                filename = unititem[1]
            except IndexError:
                pass
            unit = filename or name + '.pas'
            units.append(unit)
    units = util.uniq(units)
    return units

def find_uses(s, stripcomments=False):
    return findAbstractImports(s, parse_source.get_pUses(),
                                stripcomments=stripcomments)

def find_contains(s, stripcomments=False):
    return findAbstractImports(s, parse_source.get_pContains(),
                                stripcomments=stripcomments)

def find_includes(s, stripcomments=False):
    pInclude = parse_source.get_pInclude()

    lst = []
    for item in pInclude.scanString(s):
        toks, _, _ = item
        lst.extend(toks.asList())
    return lst

def find_resources(s, stripcomments=False):
    pResource = parse_source.get_pResource()

    lst = []
    for item in pResource.scanString(s):
        toks, _, _ = item
        lst.extend(toks.asList())
    return lst

# Delphi project files

def find_Projects(s, stripcomments=None):
    dct = parse_bds.parseBdsGroup(s)
    projects = dct.get('Projects')
    lst = []
    if projects:
        for (k,v) in projects.items():
            if k != 'Targets':
                lst.append(v)
    return lst

def find_MainSource(s, stripcomments=None):
    dct = parse_bds.parseBdsProj(s)
    source = dct.get('Source')
    lst = []
    if source:
        main_source = source.get('MainSource')
        if main_source:
            lst.append(main_source)
    return lst

def find_SearchPath(s, filepath=None, stripcomments=None):
    dct = parse_bds.parseBdsProj(s)
    dirs = dct.get('Directories')
    if dirs:
        paths_s = dirs.get('SearchPath')
        if paths_s:
            paths_s = re.sub(';$', '', paths_s)
            paths_s = paths_s.strip()
            return paths_s.split(';')
    return []

def find_UnitAliases(s, stripcomments=None):
    dct = parse_bds.parseBdsProj(s)
    comp = dct.get('Compiler')
    if comp:
        ua_s = comp.get('UnitAliases')
        if ua_s:
            return [s.split('=') for s in ua_s.split(';') if s]
    return []


if __name__ == '__main__':
    funcs_s = util.find_module_funcs_matching(__name__, '^find_')

    usage = "Usage:  %s --finder <func> file.pas" % sys.argv[0]
    optparser = OptionParser(usage=usage)
    optparser.add_option("-f", "--finder", dest="finder", metavar="function",
                         help="use finder (%s)" % funcs_s)
    (options, args) = optparser.parse_args()

    try:
        try:
            source = open(args[0]).read()
        except IndexError:
            raise model.OptionException()

        try:
            finder = options.finder
            exec('finder = find_%s' % finder)
        except NameError:
            raise model.OptionException()

        st = finder(source, stripcomments=True)
        if isinstance(st, basestring):
            sys.stdout.write(st)
        else:
            prettyprinter.pp(st)
    except model.OptionException:
        optparser.print_help()

