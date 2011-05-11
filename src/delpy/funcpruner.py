#!/usr/bin/env python
#
# Copyright: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

if __name__ == '__main__': import __path__

from optparse import OptionParser
import re
import string
import sys

from delpy import io
from delpy import util
from delpy import delphiparser
from delpy import txlparser
from delpy.delphisrc.funcprune import transformer


def inject_into_file(filepath, localname):
    tree = delphiparser.read_file(filepath)

    trans = transformer.Transformer()
    trans.listify_stmlist(tree)
    pairs = trans.inject_writeln(tree)

    delphiparser.write_file(filepath, tree)

    for (guid, funcname) in pairs:
        io.output("%s  %s\n  %s\n\n" % (guid, localname, funcname))

def prune_in_file(filepath, funclist):
    tree = delphiparser.read_file(filepath)

    trans = transformer.Transformer()
    trans.remove_funcs(tree, funclist)

    delphiparser.write_file(filepath, tree)

def inject(filepath, skiplist=None):
    filelist = txlparser.get_file_list(filepath)
    count = len(filelist)
    for (i, fp) in enumerate(filelist):
        localname = io.relpath(fp, relative_to=filepath)
        localname = localname == "." and filepath or localname
        if localname in skiplist:
            io.output("Skip file (%s/%s) %s\n" % (i+1, count, localname))
        else:
            io.output("Inject into (%s/%s) %s\n" % (i+1, count, localname))
            inject_into_file(fp, localname)

def compute_prune_list(executable, guidlistfile):
    guidlist = open(guidlistfile).read()

    rx_guid = '[0-9a-z]{8}[-][0-9a-z]{4}[-][0-9a-z]{4}[-][0-9a-z]{4}[-][0-9a-z]{12}'
    rx = '(?m)^(%s)\s+(.*)\n  (.*)\n' % rx_guid
    guiddct = {}
    filelist = []
    for (guid, filepath, funcname) in re.findall(rx, guidlist):
        filelist.append(filepath)
        guiddct[guid] = (filepath, funcname)

    data = open(executable).read()
    exeguids = re.findall(rx_guid, data)
    if not exeguids:
        io.write_result("No guids found in executable", error=True)
        sys.exit()
    for exeguid in exeguids:
        try:
            del(guiddct[exeguid])
        except KeyError: pass

    dct = {}
    for (fp, funcname) in guiddct.values():
        if fp not in dct:
            dct[fp] = []
        dct[fp].append(funcname)

    filelist = util.uniq(filelist)
    return filelist, dct

def prune(executable, guidlistfile):
    filelist, funcdict = compute_prune_list(executable, guidlistfile)

    count = sum(map(lambda x: len(x), funcdict.values()))
    i = 0
    for fp in filelist:
        if fp in funcdict:
            funclist = sorted(funcdict[fp])
            io.output("Prune in %s\n" % fp)
            for funcname in funclist:
                i += 1
                io.output(" (%s/%s) %s\n" % (i, count, funcname))
            prune_in_file(fp, funclist)


if __name__ == '__main__':
    usage = "%s  [-i <path> | -p file.exe guidlist]" % sys.argv[0]
    optparser = OptionParser(usage=usage)
    optparser.add_option("-i", "--inject", dest="inject", action="store_true",
                         help="Inject WriteLn statements")
    optparser.add_option("-p", "--prune", dest="prune", action="store_true",
                         help="Prune functions")
    optparser.add_option("", "--skiplist", dest="skiplist", action="store",
                         help="List of filenames to omit in pruning")
    (options, args) = optparser.parse_args()

    try:
        if options.inject:
            filepath = args[0]
        else:
            executable, guidlistfile = args[0], args[1]
    except IndexError:
        optparser.print_help()
        sys.exit(1)

    skiplist = []
    if options.skiplist:
        skiplist = open(options.skiplist).readlines()
        skiplist = map(string.strip, skiplist)

    if options.inject:
        inject(filepath, skiplist=skiplist)
    elif options.prune:
        prune(executable, guidlistfile)
