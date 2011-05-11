#!/usr/bin/env python
#
# Copyright: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

if __name__ == '__main__': import __path__

import os
import re
import sys

from delpy import io
from delpy.model import DelphiGraph, DelphiFile


class FileIndex(object):
    def __init__(self):
        self._index = {}

    def _prepare_path(self, fp):
        if io.platform_is_cygwin():
            fp = io.convert_path(fp)
        fp = fp.lower()
        return fp

    def has(self, fp):
        fp = self._prepare_path(fp)
        return fp in self._index

    def set(self, fp):
        fp = self._prepare_path(fp)
        self._index[fp] = None


def get_filelist_from_graph(fileindex, filepath):
    dg = DelphiGraph.from_file(filepath)
    df = dg.rootnode

    if not projectroot_path:
        projectroot_path = dg.abspath
    projectroot_path = os.path.realpath(projectroot_path)

    nodes = df.collect_nodes(DelphiFile.NodePredicates.path_not_in(dg.stdlibpath))
    # extract path to project file
    filepaths = map(lambda n: os.path.join(n.path, n.filename), nodes)

    # make absolute
    oldcwd = os.getcwd()
    io.safechdir(dg.abspath)
    filepaths = map(lambda fp: os.path.abspath(fp), filepaths)
    io.safechdir(oldcwd)

    # make relative to project root
    filepaths = map(lambda fp: io.relpath(fp, relative_to=projectroot_path),
                    filepaths)

    for fp in filepaths:
        fileindex.set(fp)

    return projectroot_path

def do_prune(projectroot_path, fileindex):
    fps = io.ifind(projectroot_path, '*')
    fps = sorted(fps, key=lambda fp:fp.lower())
    fps = map(lambda fp: io.relpath(fp, relative_to=projectroot_path), fps)

    # filter out .git/*
    fps = filter(lambda fp: not re.match('(?i)\.git', fp), fps)

    filelist = filter(lambda fp: os.path.isfile(fp), fps)
    dirlist = filter(lambda fp: os.path.isdir(fp), fps)

    for fp in filelist:
        if not fileindex.has(fp):
            print('DELETE: %s' % fp)
            os.unlink(fp)
#        else:
#            print('KEEP  : %s' % fp)

    for fp in dirlist:
        try:
            os.removedirs(fp)
            print('RMDIR : %s' % fp)
        except:
            pass
#            print('KEEP  : %s' % fp)


if __name__ == '__main__':
    fps = sys.argv[1:]
    if not fps:
        print("Usage:  %s <graph>(;<graph>)*" % sys.argv[0])
        sys.exit(1)

    fps = reduce(lambda x,y: x+y, map(lambda p: p.split(';'), fps))
    fps = filter(lambda p: p != '', fps)

    fileindex = FileIndex()
    projectroot_paths = []
    for fp in fps:
        projectroot_path = get_filelist_from_graph(fileindex, fp)
        projectroot_paths.append(projectroot_path)

    test = all(map(lambda p: p == projectroot_paths[0], projectroot_paths))
    if not test:
        print("Project root paths are not all the same, not safe to prune:\n%s"
              % "\n".join(projectroot_paths))
    else:
        projectroot_path = projectroot_paths[0]
        oldcwd = os.getcwd()
        io.safechdir(projectroot_path)
        do_prune(projectroot_path, fileindex)
        io.safechdir(oldcwd)
