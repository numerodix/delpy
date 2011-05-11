#!/usr/bin/env python
#
# Copyright: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.
#
# <desc>
# Invokes the dcc32.exe to build Delphi targets. Also uses dfmconvert.exe to
# convert dfms to binary format before running the compiler (required), but
# only if given a graph.
# Accepted inputs: graph or Delphi target (dpr, pas..)
# If running with a graph, the graph should have been built on the same
# platform, otherwise paths will not match.
# </desc>

if __name__ == '__main__': import __path__

from optparse import OptionParser
import glob
import os
import re
import shutil
import sys

from delpy import io
from delpy import util
from delpy.compilertools import DelphiCompiler
from delpy.model import FileTypes, DelphiGraph


def find_forms(graph):
    # first try to do a wide sweep finding all forms in codebase
    # this is to find forms that are pulled in from dcus which cannot be
    # traced
    projfile = os.path.join(graph.abspath, graph.rootnode.path,
                            graph.rootnode.filename)
    if projroot:
        io.write_next_action('Finding all forms in %s' % projroot)
        forms = io.ifind(projroot, '*.dfm')
        io.write_result('Found [%s]' % ', '.join(forms))
        if forms:
            return forms

    # otherwise just return all the forms in the graph
    forms = graph.rootnode.collect_nodes(lambda n: n.filetype == FileTypes.Form)
    forms = map(lambda n: os.path.join(graph.abspath, n.path, n.filename),
                forms)
    return forms

def do_dfm_conversion(transform, graph):
    forms = find_forms(graph)

    for filepath_dfm in forms:
        directory = os.path.dirname(filepath_dfm)
        filepath_dfmbin = filepath_dfm + '.bin'
        filepath_dfmtxt = filepath_dfm + '.txt'

        filename_dfm = os.path.basename(filepath_dfm)
        filename_dfmbin = os.path.basename(filepath_dfmbin)

        dfmconvert = DelphiCompiler.get_dfmconvert(relative_to=directory)
        io.run_win32app('Convert %s to binary dfm format' % filename_dfm,
                        directory,
                        [dfmconvert,
                         '--to-binary', filename_dfm,
                         '--output', filename_dfmbin])

        if os.path.exists(filepath_dfmbin):
            shutil.copymode(filepath_dfm, filepath_dfmbin)

            # make backup, file will be overwritten
            shutil.copyfile(filepath_dfm, filepath_dfmtxt)
            shutil.copymode(filepath_dfm, filepath_dfmtxt)

            # rewrite original filename
            os.unlink(filepath_dfm)
            os.rename(filepath_dfmbin, filepath_dfm)

            transform[filepath_dfm] = filepath_dfmtxt

def prepare_path(graph, use_abspath=None):
    searchpath = graph.searchpath

    # find all stdlib paths not in searchpath
    nodes = graph.rootnode.collect_nodes(lambda n: n != None)
    stdlibpath = util.iuniq(map(lambda n: n.path, nodes))
    stdlibpath = util.setminus(stdlibpath, searchpath)

    # filter stdlibpath with respect to searchpath
    if io.platform_is_cygwin():
        for path in stdlibpath:
            if io.path_cygwin_to_win(path) in searchpath:
                stdlibpath.remove(path)

    # filter for empties
    searchpath = filter(lambda p: p != '', searchpath)
    stdlibpath = filter(lambda p: p != '', stdlibpath)

    # make relative to given abspath
    if use_abspath:
        def rebase_path(path):
            oldcwd = os.getcwd()
            try:
                os.chdir(graph.abspath)
                path = os.path.abspath(path)
            finally:
                os.chdir(oldcwd)
            path = io.relpath(path, relative_to=use_abspath)
            return path
        searchpath = map(rebase_path, searchpath)
        stdlibpath = map(rebase_path, stdlibpath)

    # if cygwin make stdlibpath absolute
    if io.platform_is_cygwin():
        abs = lambda p: io.path_join(graph.abspath, p)
        stdlibpath = map(abs, stdlibpath)

    # group
    include = searchpath + stdlibpath

    # if cygwin convert to winpaths
    if io.platform_is_cygwin():
        include = map(lambda p: io.path_cygwin_to_win(p), include)

    # kill dupes
    include = util.iuniq(include)

    # join
    include_s = ';'.join(include)

    return include_s

def handle_cfg(transform, filepath):
    # if there is a .cfg file, disable it
    stem, ext = os.path.splitext(filepath)
    cfg_orig = stem + '.cfg'
    cfg_orig = io.iglob(cfg_orig)
    if cfg_orig:
        cfg_orig = cfg_orig[0]
        cfg_disable = cfg_orig + '.disable'
        io.rename(cfg_orig, cfg_disable)
        transform[cfg_orig] = cfg_disable

        # XXX write new .cfg with filtered flags
        s = open(cfg_disable).read()
        s = re.sub('(?i)-M', '', s)   # writes dcus to disk
        s = re.sub('(?i)-GD', '', s)  # writes .map file to disk
        s = re.sub('(?i)-cg', '', s)  # writes .drc file to disk
        # kill whitespace only lines
        s = '\n'.join(filter(lambda l: not re.match('^\s*$', l),
                             s.splitlines()))
        open(cfg_orig, 'w').write(s)

def do_compile(transform, abspath, relpath, filename, includepath,
               target_dir=None):
    filepath = os.path.join(abspath, relpath, filename)
    directory = os.path.dirname(filepath)

    handle_cfg(transform, filepath)

    # keep codebase clean, write output to tempdir
    tmpdir = io.get_tmpdir()
    if io.platform_is_cygwin():
        tmpdir = io.path_cygwin_to_win(tmpdir)
    target_dir = target_dir and target_dir or tmpdir
    outputdirs = [
        '-E"%s"' % target_dir, # OutputDir
        '-N"%s"' % tmpdir,     # UnitOutputDir
        '-LE"%s"' % tmpdir,    # PackageDLLOutputDir
        '-LN"%s"' % tmpdir,    # PackageDCPOutputDir
    ]

    dcc32 = DelphiCompiler.get_dcc32(relative_to=directory)
    exitcode = io.run_win32app('Building %s' % filename,
                               directory,
                               [dcc32,
#                                '--depends',
                                '-u"%s"' % includepath]
                               + outputdirs
                               + [filename])
    return exitcode

def build(filepath, use_graph=None, target_dir=None):
    transform = {}

    if not DelphiGraph.filepath_is_graph(filepath):
        fpabs = os.path.abspath(filepath)
        abspath = os.path.dirname(fpabs)
        relpath = '.'
        filename = os.path.basename(fpabs)
        stdlibpath = DelphiCompiler.get_stdlibpath(libonly=True,
                                                   relative_to=abspath)
        includepath = ';'.join(stdlibpath)

        if use_graph:
            dg = DelphiGraph.from_file(use_graph)
            df = dg.rootnode
            includepath = prepare_path(dg, use_abspath=abspath)

        return do_compile(transform, abspath, relpath, filename, includepath,
                          target_dir=target_dir)

    else:
        # load from file
        dg = DelphiGraph.from_file(filepath)
        df = dg.rootnode
        targets = df.collect_nodes(lambda n: n.filetype in (FileTypes.Program,
                                                            FileTypes.Library,
                                                            FileTypes.Package))
        target = targets[0]

        includepath = prepare_path(dg)

        try:
            # XXX seems to be redundant at times, not understood when
            do_dfm_conversion(transform, dg)
            exitcode = do_compile(transform, dg.abspath, target.path,
                                  target.filename, includepath,
                                  target_dir=target_dir)
        finally:
            for (orig, new) in transform.items():
                io.rename(new, orig)

        return exitcode


if __name__ == '__main__':
    usage = "%s  [-i <path> | -p file.exe guidlist]" % sys.argv[0]
    optparser = OptionParser(usage=usage)
    optparser.add_option("-t", "--target-dir", dest="target_dir", action="store",
                         help="Write compilation result to target_dir")
    optparser.add_option("-g", "--graph", dest="use_graph", action="store",
                         help="Use graph to extract searchpath")
    (options, args) = optparser.parse_args()

    try:
        fp = args[0]
    except IndexError:
        optparser.print_help()
        sys.exit(1)

    exitcode = build(fp,
                     use_graph=options.use_graph,
                     target_dir=options.target_dir)
    sys.exit(exitcode)
