#!/usr/bin/env python
#
# Copyright: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.
#
# <desc>
# Invokes the Delphi preprocessor dipp.exe to process the entire codebase to
# get rid of preprocessor/compiler directives, resolving conditionals and
# file includes.
# </desc>

if __name__ == '__main__': import __path__

from optparse import OptionParser
import os
import re
import sys
import uuid

from delpy import finders
from delpy import io


def get_dipp():
    # where is dipp relative to me?
    _dipp_relative_to_me = '..'
    # abspath path to dipp
    basepath_rel = os.path.join(_dipp_relative_to_me, 'dipp')
    # bin
    dipp_bin = 'dipp-1.6.1.exe'

    mypath = __file__
    distpath = os.path.dirname(os.path.abspath(os.path.realpath(mypath)))
    basepath = os.path.normpath(os.path.join(distpath, basepath_rel))
    dipp = os.path.join(basepath, dipp_bin)

    return dipp

def get_file_list(path):
    if os.path.isfile(path):
        return [path]
    filelist = io.ifind_by_exts(path, ['pas', 'dpr', 'dpk'])
    return filelist

def get_dipp_conditionals(conditionals):
    conditionals = re.sub('\r', '', conditionals)  # scrub input
    conditionals = filter(lambda c: c != '', conditionals.split(';'))

    conditionals = ';'.join(conditionals)
    conditionals = '-D%s' % conditionals

#    if ' ' in conditionals or (io.platform_is_posix() and ';' in conditionals):
#        conditionals = "'%s'" % conditionals

    return conditionals

def get_directive_checker(directives):
    directives = re.sub('\r', '', directives)  # scrub input
    directives = filter(lambda c: c != '', directives.split(';'))
    index = {}
    for directive in directives:
        value = False
        if directive[-1] == '+':
            value = True
        index[directive[0]] = value

    def is_directive_on(directive):
        return index[directive[0]]

    return is_directive_on

def prepare_to_preprocess(is_directive_on, filepath):
    ''' {$IFOPT N+} -> {$IFDEF SOMETHING} '''
    s = open(filepath).read()

    t = []

    cursor = 0
    for m in re.finditer('(?i)[{][$]IFOPT ([A-Za-z+-]+)[}]', s):
        flag = m.group(1)

        hex = uuid.uuid4().hex
        hex = re.sub('^[0-9]*', '', hex)[:10]

        newcond = '{$IFDEF %s}' % hex
        if is_directive_on(flag):
            newcond = '{$DEFINE %s}%s{$UNDEF %s}' % (hex, newcond, hex)

        t.append( s[cursor:m.start()] )
        t.append( newcond )
        cursor = m.end()
    t.append( s[cursor:] )

    t = ''.join(t)
    open(filepath, 'w').write(t)

def do_after_preprocess(filepath):
    s = open(filepath).read()

    # strip comments and all directives except those without which a build
    # cannot succeed
    s = finders.find_stripCommentsKeepAllDirectives(s)

    # unify line endings
    s = finders.find_unifyNewlines(s)

    open(filepath, 'w').write(s)

def do_preprocess(filelist, is_directive_on, dipp_conditionals):
    dipp_bin = get_dipp()

    for fp in filelist:
        filename = os.path.basename(fp)
        directory = os.path.dirname(fp)

        tmpfile = io.get_tmpfile(filename)
        if io.platform_is_cygwin():
            tmpfile = io.path_cygwin_to_win(tmpfile)

        ### PASS 1
        flags = ['-o', '-PD2006', '-li']

        exitcode = io.run_win32app('Preprocessing includes in %s' % fp,
                                   directory,
                                   [dipp_bin, filename, tmpfile]
                                   + flags)
        if not exitcode:
            io.rename(tmpfile, fp)
        else:
            return exitcode

        ### PASS 1.5
        prepare_to_preprocess(is_directive_on, fp)

        ### PASS 2
        flags = ['-o', '-PD2006', '-c', '-h', dipp_conditionals]

        exitcode = io.run_win32app('Preprocessing conditionals in %s' % fp,
                                   directory,
                                   [dipp_bin, filename, tmpfile]
                                   + flags)
        if not exitcode:
            io.rename(tmpfile, fp)
        else:
            return exitcode

        ### PASS 2.5
        do_after_preprocess(fp)

    return exitcode

def main(filepath, directives, conditionals):
    filelist = get_file_list(filepath)
    is_directive_on = get_directive_checker(directives)
    dipp_conditionals = get_dipp_conditionals(conditionals)
    return do_preprocess(filelist, is_directive_on, dipp_conditionals)


if __name__ == '__main__':
    usage = "Usage:  %s <file|dir> [options]" % sys.argv[0] 
    optparser = OptionParser(usage=usage)
    optparser.add_option("-d", "--directives", metavar="directives",
                         type="string", help="compiler directives, eg: H-;R+")
    optparser.add_option("-c", "--conditionals", metavar="conditionals",
                         type="string", help="compiler conditionals, eg: WIN32;DEBUG")
    (options, args) = optparser.parse_args()

    try:
        filepath = args[0]
    except IndexError:
        optparser.print_help()
        sys.exit(1)

    directives = options.directives or ''
    conditionals = options.conditionals or ''

    exitcode = main(filepath, directives, conditionals)
    sys.exit(exitcode)
