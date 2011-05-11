#!/usr/bin/env python
#
# Copyright: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.
#
# <desc>
# A diff for graphs, shows differences between two graphs.
# </desc>

if __name__ == '__main__': import __path__

import sys
import util

from delpy import io
from delpy.model import DelphiGraph

from delpy.lib import ansicolor

def fmt_obj(obj, w):
    ss = []
    if not hasattr(obj, '__iter__'):
        obj = [obj]
    for o in obj:
        ss.append( (str(o) or '<empty string>').ljust(w) )
    return ss

def get_len(lst, std_len):
    l = util.longest(lst)
    l = l < std_len and std_len or l
    return l

def show_sidebyside(att, fsts, snds, ws, colors):
    s = ''
    keyw, fstw, sndw = ws
    color1, color2 = colors

    num = max(len(fsts), len(snds))
    for i in range(num):
        val1 = util.safeindex(fsts, i, '') or ' '*fstw
        val2 = util.safeindex(snds, i, '') or ' '*sndw

        if i == 0:
            s += '%s>  ' % att.ljust(keyw)
        else:
            s += '%s|  ' % ''.ljust(keyw)

        if val1 != val2:
            val1 = color1(val1)
            val2 = color2(val2)

        s += '%s  ' % val1
        s += '%s  \n' % val2
    return s

def show_oneafterother(att, fsts, snds, ws, colors):
    def prompt(att, keyw, marker=[]):
        '''Use keyword initialization quirk to get different result on the
        first call'''
        if not marker:
            s = '%s>' % att.ljust(keyw)
        else:
            s = '%s|' % ''.ljust(keyw)
        marker.append(None)
        return s

    keyw, fstw, sndw = ws
    color1, color2 = colors

    s = ''
    for val1 in fsts:
        s += '%s  %s\n' % (prompt(att, keyw), color1('- ' + val1))
    for val2 in snds:
        s += '%s  %s\n' % (prompt(att, keyw), color2('+ ' + val2))
    return s

def show_diff(filepath1, filepath2):
    graph1 = DelphiGraph.from_file(filepath1)
    graph2 = DelphiGraph.from_file(filepath2)

    color_title = ansicolor.magenta
    color1 = ansicolor.cyan
    color2 = ansicolor.yellow

    keyw_def, fstw_def, sndw_def = 10, 30, 30
    
    diffs = DelphiGraph.diff_graphs(graph1, graph2)

    exit = 0
    if diffs:
        exit = 1
        io.output('Showing diff between:\n')
        io.output(' - %s\n' % color1(filepath1))
        io.output(' - %s\n' % color2(filepath2))

        for diff in diffs:
            io.output(color_title('>>> File: %s\n' % diff.name))

            keyw = get_len(diff.keys(), keyw_def)

            for att, val in diff.iteritems():
                fst, snd = val

                fsts = fmt_obj(fst, fstw_def)
                snds = fmt_obj(snd, sndw_def)

                fstw = get_len(fsts, fstw_def)
                sndw = get_len(snds, sndw_def)

                if fstw <= fstw_def and sndw <= sndw_def:
                    s = show_sidebyside(att, fsts, snds, (keyw,fstw,sndw),
                                        (color1,color2))
                else:
                    s = show_oneafterother(att, fsts, snds, (keyw,fstw,sndw),
                                           (color1,color2))
                io.output(s)

    return exit

if __name__ == '__main__':
    fp1 = sys.argv[1]
    fp2 = sys.argv[2]
    exit = show_diff(fp1, fp2)
    sys.exit(exit)
