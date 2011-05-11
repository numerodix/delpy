#!/usr/bin/env python
#
# Copyright: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

if __name__ == '__main__': import __path__

import os
import pstats
import sys
import traceback

from delpy import io


def trace_func(f):
    def __prof_dec(*a, **kw):
        value = f(*a, **kw)
        if len(a) > 1:
            arg = a[1]
        if arg == value:
            print f.__name__, arg, value
            stack = traceback.extract_stack(limit=20)
            for l in traceback.format_list(stack):
                if not '__prof_dec' in l:
                    print l
        return value
    return __prof_dec

def strip_dirs(fp):
    '''Strip directory paths in function listing'''
    p = pstats.Stats(fp)
    p = p.strip_dirs()
    p.dump_stats(fp)

def output(fp):
    p = pstats.Stats(fp)
    p.sort_stats('cumulative').print_stats(10)
    p.sort_stats('time').print_stats(10)

def main(args):
    prog = args.pop(0)
    # try to locate prog on same path as sys.argv[0]
    if not os.path.exists(prog):
        path = os.path.dirname(os.path.abspath(sys.argv[0]))
        prog = os.path.join(path, prog)
        if not os.path.exists(prog):
            io.write_result('Not found: %s' % os.path.basename(prog),
                            error=True)
            return

    fp = io.get_tmpfile(os.path.basename(prog) + '.profile')

    args = ['python', '-m', 'cProfile', '-o', fp, prog] + args
    io.invoke(args)

    strip_dirs(fp)
    output(fp)


if __name__ == '__main__':
    fst = sys.argv[1]
    _, ext = os.path.splitext(fst)
    if ext == '.profile':
        output(fst)
    else:
        main(sys.argv[1:])
