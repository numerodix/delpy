#!/usr/bin/env python
#
# Copyright: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.
#
# <desc>
# Administrates the local copy of BDS: the compiler dcc32.exe and the
# standard libraries (dcu and pas): installing it, checking the install
# and returning a stdlibpath.
# </desc>

if __name__ == '__main__': import __path__

import os
import re
import shutil
import stat
import sys

from delpy import io
from delpy import util

help = '''\
Files needed from the Borland Delphi distribution (on path %s), to be
placed in directories under the base directory (%s):

%s
To install the missing tools:
 %s ${BDS}
'''

class DelphiCompiler(object):
    bds = '${BDS}'

    # where is dcc32 relative to me?
    _dcc_relative_to_me = '..'
    _dfmconvert_relative_to_me = '..'
    _txl_relative_to_me = '..'
    # abspath path to dcc32
    basepath_dcc_rel = os.path.join(_dcc_relative_to_me, 'dcc32')
    basepath_dfmconvert_rel = os.path.join(_dfmconvert_relative_to_me,
                                           'dfmconvert')
    basepath_txlbin_rel = os.path.join(_txl_relative_to_me, 'txl')
    basepath_txlgram_rel = os.path.join(_txl_relative_to_me, 'txl', 'delphi')

    dcc32_binary = 'DCC32.EXE'
    dfmconvert_binary = 'dfmconvert.exe'
    txl_binary_linux = ['dist-linux', 'bin', 'txl']
    txl_binary_win = ['dist-win', 'bin', 'txl']

    tree = {
        ('Bin', dcc32_binary):      ('bin', dcc32_binary),
        ('Bin', 'borlndmm.dll'):    ('bin', 'borlndmm.dll'),
        ('Bin', 'rlink32.dll'):     ('bin', 'rlink32.dll'),
        ('lib', '**'):              ('lib', '**'),
        ('source', '**'):           ('src', '**'),
    }

    @classmethod
    def pathmerge(cls, basepath, parts, strict=False):
        parts = list(parts)
        if strict and '*' in parts[-1]:
            parts = parts[:-1]
        parts.insert(0, basepath)
        path = os.path.join(*parts)
        return path

    @classmethod
    def write_notice(cls):
        s = ''
        for (src, trg) in sorted(cls.tree.items()):
            src = cls.pathmerge(cls.bds, src)
            trg = cls.pathmerge(cls.get_basepath(cls.basepath_dcc_rel), trg)
            s += '%s  ->  %s\n' % (src.ljust(35), trg)
        s = help % (cls.bds, cls.get_basepath(cls.basepath_dcc_rel), s, sys.argv[0])
        io.write(s)

    @classmethod
    def check(cls):
        result = True
        for (src, trg) in sorted(cls.tree.items()):
            trg = cls.pathmerge(cls.get_basepath(cls.basepath_dcc_rel), trg, strict=True)
            if not os.path.exists(trg):
                result = False
                io.write_result("Missing: %s" % trg, error=True)
        return result

    @classmethod
    def install(cls, bds):
        for (src, trg) in sorted(cls.tree.items()):
            src = cls.pathmerge(bds, src, strict=True)
            trg = cls.pathmerge(cls.get_basepath(cls.basepath_dcc_rel), trg, strict=True)
            io.write('%s  ->  %s\n' % (src, trg))
            if os.path.isdir(src):
                shutil.copytree(src, trg)
            else:
                io.mkdir_p(os.path.dirname(trg))
                shutil.copyfile(src, trg)

        # chmod generously just in case we get permission errors
        io.chmod_R(cls.get_basepath(cls.basepath_dcc_rel),
                   stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)

    @classmethod
    def get_basepath(cls, basepath, relative_to=None):
        mypath = __file__
        distpath = os.path.dirname(os.path.abspath(mypath))
        basepath = os.path.normpath(os.path.join(distpath, basepath))
        if relative_to:
            basepath = io.relpath(basepath, relative_to)
        return basepath

    @classmethod
    def get_stdlibpath(cls, src_first=False, libonly=False, relative_to=None):
        containers = ('lib', 'src')
        if src_first:
            containers = ('src', 'lib')
        if libonly:
            containers = ('lib',)

        stdlibpath = []
        for cont in containers:
            basepath = cls.get_basepath(cls.basepath_dcc_rel)
            cont = os.path.join(basepath, cont)
            stdlibpath.append(cont)
            for root, dirs, files in os.walk(cont):
                for d in dirs:
                    # skip debug dir, has dcus with debug info
                    if not (re.match('(?i)debug', d) or
                            re.search('(?i)debug', root)):
                        stdlibpath.append(os.path.join(root, d))
        if relative_to:
            for (i, path) in enumerate(stdlibpath):
                stdlibpath[i] = io.relpath(path, relative_to)
        return stdlibpath

    @classmethod
    def get_dfmconvert(cls, relative_to=None):
        # XXX on cygwin invocation seems to fail sometimes with a rel path
        if io.platform_is_cygwin():
            relative_to = None
        return os.path.join(cls.get_basepath(cls.basepath_dfmconvert_rel,
                                             relative_to=relative_to),
                            cls.dfmconvert_binary)

    @classmethod
    def get_dcc32(cls, relative_to=None):
        # XXX on cygwin invocation seems to fail sometimes with a rel path
        if io.platform_is_cygwin():
            relative_to = None
        return os.path.join(cls.get_basepath(cls.basepath_dcc_rel,
                                             relative_to=relative_to),
                            'bin', cls.dcc32_binary)

    @classmethod
    def get_txl_binary(cls, relative_to=None):
        txl_binary = cls.txl_binary_win
        if io.platform_is_linux():
            txl_binary = cls.txl_binary_linux
        return os.path.join(cls.get_basepath(cls.basepath_txlbin_rel,
                                             relative_to=relative_to),
                            *txl_binary)

    @classmethod
    def get_txl_grammar_path(cls, relative_to=None):
        # XXX on cygwin invocation seems to fail sometimes with a rel path
        if io.platform_is_cygwin():
            relative_to = None
        return cls.get_basepath(cls.basepath_txlgram_rel,
                                relative_to=relative_to)

    @classmethod
    def get_dcc_charset(cls):
        "Charset to expect in delphi code"
        return "iso-8859-1"

if __name__ == '__main__':
    if '-h' in sys.argv:
        DelphiCompiler.write_notice()
        sys.exit()

    if len(sys.argv) > 1:
        bds_path = sys.argv[1]
        DelphiCompiler.install(bds_path)
    else:
        result = DelphiCompiler.check()
        if not result:
            DelphiCompiler.write_notice()
