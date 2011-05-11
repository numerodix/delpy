#!/usr/bin/env python
#
# Copyright: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

if __name__ == '__main__': import __path__

from optparse import OptionParser
import os
import re
import sys

from delpy import io
from delpy.compilertools import DelphiCompiler

__all__ = ['get_file_list', 'parse_file']

class TXLParser(object):
    grammar = 'pas.txl'
    memalloc_size = 1000

    @classmethod
    def get_txl_prog(cls):
        grammar_path = DelphiCompiler.get_txl_grammar_path(relative_to=directory)
        txlprog = os.path.join(grammar_path, txlprog)
        return txlprog

    @classmethod
    def exec_txl(cls, txlprog, filepath, txlargs=None):
        directory, filename = os.path.split(filepath)
        directory = directory and directory or "."

        txlbin = DelphiCompiler.get_txl_binary(relative_to=directory)
        grammar_path = DelphiCompiler.get_txl_grammar_path(relative_to=directory)

        txlprog = os.path.join(grammar_path, txlprog)
        if not io.platform_is_linux():
            txlprog = io.path_cygwin_to_win(txlprog)

        txlargs = txlargs and txlargs or []

        return io.invoke([txlbin] + txlargs + [txlprog, filename],
                         cwd=directory, return_all=True)

    @classmethod
    def exec_gracefully(cls, filepath, args=None):
        args = args and args or []

        memargs = ['-s', str(cls.memalloc_size)]
        combinations = [
            ('expanded', [cls.grammar, filepath, args]),
            ('memalloc', [cls.grammar, filepath, args + memargs]),
        ]

        label = 'failed'
        for comb_name, comb_value in combinations:
            ret, out, err = cls.exec_txl(*comb_value)
            if ret == 0:
                label = comb_name
                break

        return ret == 0, label, out, err

    @classmethod
    def parse_test(cls, filepath, unparse=False):
        filelist = get_file_list(filepath)

        failures = 0
        for fp in filelist:
            success, lab, out, err = cls.exec_gracefully(fp)
            if not success:
                failures += 1
            elif unparse:
                s = out[-1] == "\n" and out or out + "\n"
                open(fp, 'w').write(s)
            localname = io.relpath(fp, relative_to=filepath)
            localname = localname == "." and filepath or localname
            io.output("%-9.9s  %s\n" % (lab.upper(), localname))
        io.output("Processed %s files, %s failed\n" % (len(filelist), failures))

        exitcode = failures > 0 and 1 or 0
        return exitcode

    @classmethod
    def parse_to_xml(cls, filepath, verbose_error=False):
        success, lab, out, err = cls.exec_gracefully(filepath, args=['-xml'])

        if not success:
            io.write_result("Failed to parse %s" % filepath, error=True)
            if verbose_error:
                io.output(err)
        else:
            xml = out + "\n"
            return xml


def get_file_list(path):
    if os.path.isfile(path):
        return [path]
    filelist = io.ifind_by_exts(path, ['pas', 'dpr', 'dpk'])
    return filelist

def parse_file(filepath):
    return TXLParser.parse_to_xml(filepath)


if __name__ == '__main__':
    usage = "%s  <path>" % sys.argv[0]
    optparser = OptionParser(usage=usage)
    optparser.add_option("-v", "", dest="verbose_error", action="store_true",
                         help="Display verbose errors")
    optparser.add_option("", "--parsetest", dest="parse_test", action="store_true",
                         help="Test TXL parser on input")
    optparser.add_option("", "--parsetest-unparse", dest="parse_test_unparse",
                         action="store_true", help="Parse and unparse using TXL")
    (options, args) = optparser.parse_args()

    try:
        filepath = args[0]
    except IndexError:
        optparser.print_help()
        sys.exit(1)

    if options.parse_test or options.parse_test_unparse:
        unparse = False
        if options.parse_test_unparse:
            unparse = True
        exitcode = TXLParser.parse_test(filepath, unparse=unparse)
        sys.exit(exitcode)
    else:
        xml = TXLParser.parse_to_xml(filepath,
                                     verbose_error=options.verbose_error)
        if xml:
            io.output(xml)
