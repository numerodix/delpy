#!/usr/bin/env python
#
# Copyright: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.
#
# <desc>
# Recursively explores a codebase finding project files, targets etc. Can also
# trace them.
# </desc>

if __name__ == '__main__': import __path__

import os
import re
import sys
import traceback

from delpy import finders
from delpy import io
from delpy import makedelphi
from delpy import trace_program
from delpy import util
from delpy.model import Categories, FileTypes, DelphiGraph


def classify_file(filepath):
    """Parsing is too slow, guess by extension unless filetype is ambiguous"""
    # XXX very similar to classify_file in trace_program
    filetypes = FileTypes.get_filetypes_from_extension(filepath)
    filetype = filetypes[0]

    # filetype is ambiguous
    if len(filetypes) > 1:
        if os.path.exists(filepath) and FileTypes.is_source_file(filepath):
            filecontent = open(filepath).read()
            header = finders.find_programHeader(filecontent, stripcomments=True)
            if header:
                source_type_name, _ = header
                filetype = FileTypes.get_filetype_from_source_name(source_type_name)

    return filetype

def traverse(directory, index):
    for item in os.listdir(directory):
        itempath = os.path.join(directory, item)
        if os.path.isfile(itempath):
            filetype = classify_file(itempath)
            if filetype not in index:
                index[filetype] = []
            index[filetype].append(itempath)
        elif os.path.isdir(itempath):
            traverse(itempath, index)

def normalize_filepath(fp):
    # make sure filepaths garnered from graph and file system are equal
    return os.path.normpath(fp.lower())

def get_graph_filepaths(graph, relative_to):
    ns = graph.rootnode.collect_nodes(lambda n: n)
    f = lambda n: io.relpath(os.path.join(graph.abspath, n.path, n.filename),
                             relative_to)
    filepaths = map(f, ns)
    filepaths = map(normalize_filepath, filepaths)
    return filepaths

def filter_index_by_graph(index, graph, excludes):
    # filter index for files contained in graph
    fps = get_graph_filepaths(graph, os.getcwd())
    for ft in index:
        # don't subsume the top nodes
        if ft in excludes:
            continue
        index[ft] = filter(lambda fp: normalize_filepath(fp) not in fps,
                           index[ft])

def process(index, graphs, trace=False):
    def output(s):
        if not trace:
            io.write(s)

    order = FileTypes.get_filetypes_by_build_target()
    for filetype in order:
        items = index.get(filetype, [])
        items = util.isort(items)
        if items:
            output('%s:\n' % filetype.name)
        for item in items:
            line = '- %s\n' % item
            output(line)
            if trace:
                graph_fp = trace_file(item, filetype)
                graph = DelphiGraph.from_file(graph_fp)
                graphs[item] = graph

                filter_index_by_graph(index, graph,
                                      excludes=[FileTypes.DelphiProjectGroup,
                                                FileTypes.DelphiProject,
                                                FileTypes.Program,
                                                FileTypes.Library,
                                                FileTypes.Package])

def trace_file(fp, filetype):
    try:
        projview = False
        if filetype == FileTypes.DelphiProjectGroup:
            projview = True
        return trace_program.DepTracer().trace_write(fp, projview=projview,
                                                  noclobber=True)
    except:
        s = traceback.format_exc()
        f = os.path.basename(fp)
        open(io.get_tmpfile('%s.explore_errors' % f,), 'a').write(s)

def get_explore_report(index, graphs):
    s = 'Graphs:\n'
    order = FileTypes.get_filetypes_by_build_target()
    for filetype in order:
        items = index.get(filetype, [])
        items = util.isort(items)
        for item in items:
            dg = graphs.get(item)
            filter_index_by_graph(index, dg, excludes=[])
            if dg:
                df = dg.rootnode

                def set_path(node):
                    node.path = io.relpath(os.path.join(dg.abspath, node.path),
                                           relative_to=os.getcwd())
                    return True
                set_path(df)
                df.filter_nodes(set_path)

                df.filter_nodes(lambda n: n.filetype in order)
            s += '\n'.join(collect_nodes(df)) + '\n'

    t = ''
    order = FileTypes.get_filetypes_by_category(Categories.Source)
    for filetype in order:
        items = index.get(filetype, [])
        items = util.isort(items)
        if items:
            t += '= %s =\n' % filetype.name
        for item in items:
            t += '- %s\n' % item
    if t:
        s += '\nLoose files:\n'
        s += t

    return s

def collect_nodes(node):
    rootnode = node
    nodes = ['= %s =' % node.filepath]
    def f(node, children, depth):
        if node is not rootnode:
            nodes.append('%s %s' % ((depth+1)*'-', node.filepath))
    node.walk(f, recursive_cache=True)
    return nodes

def write_report(directory, report):
    io.write(report) # write to screen for convenience?

    pathname = os.path.basename(os.path.abspath(directory))
    fp = io.get_tmpfile('%s.explore_codebase' % pathname, noclobber=True)
    open(fp, 'w').write(report)
    io.write_result("Wrote file %s ." % fp)


if __name__ == '__main__':
    directory = sys.argv[1]
    trace = '-t' in sys.argv

    index = {}
    traverse(directory, index)
    graphs = {}
    process(index, graphs, trace=trace)
    if trace:
        report = get_explore_report(index, graphs)
        write_report(directory, report)
