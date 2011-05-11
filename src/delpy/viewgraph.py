#!/usr/bin/env python
#
# Copyright: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.
#
# <desc>
# Dep tracer to build a graph of import statements between Delphi source files,
# given a specific Delphi target (bdsgroup, bdsproj, dpr, pas..)
# </desc>

if __name__ == '__main__': import __path__

from optparse import OptionParser
import os
import sys

from delpy.lib import prettyprinter

from delpy import io
from delpy import dotgenerator
from delpy.model import DelphiGraph, DelphiFile, FileTypes, OptionException
from delpy.trace_program import DepTracer


def get_graph(filepath, prefilter=None, maxdepth=None):
    if not DelphiGraph.filepath_is_graph(filepath):
        # pre filter
        projview = False
        if prefilter: # projview
            projview = True

        # trace
        tracer = DepTracer()
        filepath = tracer.trace_write(filepath, maxdepth=maxdepth, projview=projview)
    # load from file
    dg = DelphiGraph.from_file(filepath)
    return dg

def master(filepath, prefilter, postfilter, maxdepth=None):
    dg = get_graph(filepath, prefilter=prefilter, maxdepth=maxdepth)
    df = dg.rootnode

    # post filter
    if not flags['dcu']:
        df.filter_nodes(DelphiFile.NodePredicates.is_not_dcu)
    if not flags['obj']:
        df.filter_nodes(DelphiFile.NodePredicates.is_not_obj)
    if not flags['stdlib']:
        df.filter_nodes(DelphiFile.NodePredicates.path_not_in(dg.stdlibpath))
    if not flags['resources']:
        df.filter_nodes(DelphiFile.NodePredicates.is_not_resource)

    return dg

def ls(graph):
    df = dg.rootnode
    nodes = df.collect_nodes(DelphiFile.NodePredicates.true)
    for n in nodes:
        io.output("%s\n" % n.filepath)

def ls_abspath(graph):
    path = dg.abspath
    io.output("%s\n" % path)

def ls_searchpath(graph):
    for path in graph.searchpath:
        io.output("%s\n" % path)

def ls_stdlibpath(graph):
    for path in graph.stdlibpath:
        io.output("%s\n" % path)

def lint(graph):
    def get_abs_searchpath(searchpath):
        paths = []
        for path in searchpath:
            if io.path_is_abs(path):
                paths.append(path)
        return paths

    df = graph.rootnode

    abspaths = get_abs_searchpath(graph.searchpath)
    notfounds = df.collect_nodes(DelphiFile.NodePredicates.file_notexists)
    notfounds = map(lambda n: n.filepath, notfounds)

    exit = 0
    if abspaths or notfounds:
        exit = 1
        if abspaths:
            io.output('Searchpath paths not relative:\n')
            for path in abspaths:
                io.output(' * %s\n' % path)

        if notfounds:
            io.output('Files not found:\n')
            for fp in notfounds:
                io.output(' * %s\n' % fp)

    return exit

def verify(graph):
    df = graph.rootnode

    nodes = df.collect_nodes(DelphiFile.NodePredicates.path_not_in(graph.stdlibpath))
    # if the file wasn't found during indexing there is no point complaining
    # about it now
    nodes = filter(lambda n: n.exists, nodes)
    fps = map(lambda n: n.filepath, nodes)

    notfounds = []
    exit = 0

    for fp in fps:
        if not io.ifile_exists(os.path.join(graph.abspath, fp)):
            notfounds.append(fp)

    if notfounds:
        exit = 1
        io.output('Files not found:\n')
        for fp in notfounds:
            io.output(' * %s\n' % fp)

    return exit


if __name__ == '__main__':
    usage = "Usage:  %s [file.pas|name.graph]" % sys.argv[0]
    usage += "\n\nPipeline principle:"
    usage += "\n    1. trace codebase starting from file.pas"
    usage += "\n      <filter collection process>"
    usage += "\n    2. produce name.graph, write to disk"
    usage += "\n      <filter graph>"
    usage += "\n    3. read name.graph, display dot"

    optparser = OptionParser(usage=usage)
    optparser.add_option("-p", "--projview", dest="projview",
                         action="store_true",
                         help="only recurse to program/library depth")
    optparser.add_option("-d", "--depth", dest="depth", type="int",
                         metavar="depth", help="trace depth (integer >0)")
    optparser.add_option("-q", "", dest="quiet", action="store_true",
                         help="no action after writing .graph file")
    optparser.add_option("-v", "", dest="write", action="store_true",
                         help="dump graph to output")
    optparser.add_option("", "--ls", dest="ls", action="store_true",
                         help="list files in graph")
    optparser.add_option("", "--ls-abspath", dest="ls_abspath", action="store_true",
                         help="display abspath to root node")
    optparser.add_option("", "--ls-searchpath", dest="ls_searchpath", action="store_true",
                         help="display searchpath")
    optparser.add_option("", "--ls-stdlibpath", dest="ls_stdlibpath", action="store_true",
                         help="display stdlibpath")
    optparser.add_option("", "--lint", dest="lint", action="store_true",
                         help="check graph for common errors")
    optparser.add_option("", "--verify", dest="verify", action="store_true",
                         help="verify that files in the graph are on disk")
    optparser.add_option("", "--dot", dest="dotfile",
                         metavar="file", help="write dot to file")
    optparser.add_option("", "--all", action="store_true",
                         help="don't filter any files (below)")

    flags = {
        'resources': False,
        'stdlib': False,
        'dcu': True,
        'obj': False,
    }
    for (k,v) in flags.items():
        optparser.add_option("", "--%s" % k, dest=k, action="store_true", help=(v and "default" or ""))
        optparser.add_option("", "--no-%s" % k, dest=k, action="store_false", help=(not v and "default" or ""))
    (options, args) = optparser.parse_args()

    for k in flags:
        if hasattr(options, k):
            v = getattr(options, k)
            if v != None:
                flags[k] = v
    if options.all or options.lint:  # if lint, don't filter anything
        flags = flags.fromkeys(flags, True)

    try:
        try:
            filepath = args[0]
        except IndexError:
            raise OptionException()

        dg = master(filepath, options.projview, flags, maxdepth=options.depth)
        if options.quiet:
            pass  # do nothing, avoid else clause below
        elif options.write:
            prettyprinter.pp(dg, collapse_duplicates=True)
        elif options.ls:
            ls(dg)
        elif options.ls_abspath:
            ls_abspath(dg)
        elif options.ls_searchpath:
            ls_searchpath(dg)
        elif options.ls_stdlibpath:
            ls_stdlibpath(dg)
        elif options.lint:
            sys.exit(lint(dg))
        elif options.verify:
            sys.exit(verify(dg))
        elif options.dotfile:
            fp = options.dotfile
            _, ext = os.path.splitext(fp)
            if ext != '.dot':
                fp = fp + '.dot'
            dotgenerator.DotGenerator(dg).write_dot('.', fp)
        else:
            dotgenerator.DotGenerator(dg).show_dot()
    except OptionException:
        optparser.print_help()
