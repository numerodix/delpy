#!/usr/bin/env python
#
# Copyright: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

if __name__ == '__main__': import __path__

import os
import re
import sys

from delpy.lib import prettyprinter

from delpy import dotgenerator
from delpy import finders
from delpy import io
from delpy import util
from delpy.compilertools import DelphiCompiler
from delpy.model import FileTypes, FileIndex, DelphiFile, DelphiGraph


def match_file(filepath):
    fp = filepath
    exists = io.ifile_exists(fp)
    if not exists:
        stem, ext = os.path.splitext(fp)
        if ext.lower() == '.pas':
            fp = stem + '.dcu'
            exists = io.ifile_exists(fp)
    return exists and (True, fp) or (False, filepath)

def locate_file(filepath, paths):
    exists, filepath = match_file(filepath)
    if not exists:
        filename = os.path.basename(filepath)
        for p in paths:
            filepath = os.path.join(p, filename)
            exists, filepath = match_file(filepath)
            if exists:
                break
    return exists and filepath or None

def classify_file(filepath, searchpath, stdlibpath):
    located = locate_file(filepath, searchpath + stdlibpath)
    filepath = located and located or filepath
    exists = located and True or False

    # XXX if the filetype is ambiguous and the file is not found there is no way to
    # decide its filetype, just pick the first filetype from the list
    filetypes = FileTypes.get_filetypes_from_extension(filepath)
    filetype = filetypes[0]

    if exists and FileTypes.is_source_file(filepath):
        filepaths = io.iglob(filepath)
        filepath = filepaths[0]
        filecontent = open(filepath).read()
        header = finders.find_programHeader(filecontent, stripcomments=True)
        if header:
            source_type_name, _ = header
            filetype = FileTypes.get_filetype_from_source_name(source_type_name)
    return filepath, exists, filetype

def process_filepaths(curpath, unitaliases, fps):
    # resolve unit aliases
    nfps = []
    for fp in fps:
        stem, ext = os.path.splitext(fp)
        stem = stem.lower()
        if ext in ('.pas', '.dcu') and stem in unitaliases:
            nfps.append(unitaliases[stem] + ext)
        else:
            nfps.append(fp)
    fps = util.uniq(nfps)

    fps = [io.convert_path(fp) for fp in fps]
    fps = map(lambda f: os.path.join(curpath, f), fps)
    fps = map(lambda f: os.path.normpath(f), fps)
    fps = io.iglobs(fps)
    fps = util.uniq(fps)
    return fps

def collect_searchpath(searchpath, delphifile, filepath):
    if delphifile.filetype == FileTypes.DelphiProject:
        sp = finders.find_SearchPath(open(filepath).read(), filepath=filepath)
        curpath = delphifile.path
        for p in sp:
            if io.platform_is_posix() and io.path_is_win(p):
                p = io.path_win_to_posix(p)
            p = os.path.join(curpath, p)
            p = os.path.normpath(p)
            searchpath.append(p)
        searchpath = util.iuniq(searchpath)
    return searchpath

def collect_unitaliases(unitaliases, delphifile, filepath):
    if delphifile.filetype == FileTypes.DelphiProject:
        uas = finders.find_UnitAliases(open(filepath).read())
        for ua in uas:
            k, v = ua
            k = k.lower()
            unitaliases[k] = v
    return unitaliases

def findUses(s, **kw):
    return finders.find_uses(s, stripcomments=True)

def findContains(s, **kw):
    return finders.find_contains(s, stripcomments=True)

def findIncludes(s, **kw):
    return finders.find_includes(s, stripcomments=True)

def findResources(s, **kw):
    '''A wildcard in a {$R *.res} or {$R *.dfm} directive is not a wildcard,
    is not matched with a glob, it only means Form.dfm if found in Form.pas'''
    # XXX the context of files found as resources is not kept, which makes
    # file extensions that do not map to known resources (.res, .frm) become
    # classified as Unknown filetype
    ress = finders.find_resources(s)
    for (i, res) in enumerate(ress):
        res = io.convert_path(res)
        path, filename = os.path.split(res)
        stem, ext = os.path.splitext(filename)
        if stem == '*':
            par, _ = os.path.splitext(kw['parent'].filename)
            stem = par
            ress[i] = os.path.join(path, stem + ext)
    return ress

def findDelphiCompilerFlags(s, **kw):
    par, _ = os.path.splitext(kw['parent'].filename)
    cfg_file = par + FileTypes.DelphiCompilerFlags.extension
    return [cfg_file]

def findMainSource(s, **kw):
    return finders.find_MainSource(s)

def findProjects(s, **kw):
    return finders.find_Projects(s)

def group(*fs, **kw):
    return lambda s, **kw: reduce(lambda x,y: x+y, [f(s, **kw) for f in fs])

class DepTracer(FileIndex):
    def __init__(self):
        super(self.__class__, self).__init__()

    def new_delphifile(self, filepath, args):
        delphifile = DelphiFile(*args)
        self.index_set(filepath, delphifile)
        return delphifile

    def trace(self, filepath, maxdepth=None, projview=False):
        def trace_deps(filepath, searchpath, stdlibpath, unitaliases,
                       depth=0, maxdepth=None):
            # don't prevent calls on filepaths already in index so as to resolve
            # cycles properly, but catch these here to return a valid object
            # for a filepath already known
            if self.index_has(filepath):
                return self.index_get(filepath)

            io.write_next_action("Tracing %s" % os.path.basename(filepath),
                                                                 indent=depth)

            filepath, exists, filetype = classify_file(filepath, searchpath,
                                                       stdlibpath)
            delphifile = self.new_delphifile(filepath,
                                             (filepath, exists, filetype))
            if exists:
                searchpath = collect_searchpath(searchpath, delphifile,
                                                filepath)
                unitaliases = collect_unitaliases(unitaliases, delphifile,
                                                  filepath)
                finder_function = finder_dispatch.get(filetype)
                if finder_function:
                    fps = finder_function(open(filepath).read(),
                                          parent=delphifile)
                    io.write_result('Found [%s]' % ', '.join(fps), indent=depth)
                    fps = process_filepaths(delphifile.path, unitaliases, fps)
                    if not maxdepth or maxdepth >= depth+1:
                        for fp in fps:
                            delphifile.add_node(trace_deps(fp,
                                                           searchpath,
                                                           stdlibpath,
                                                           unitaliases,
                                                           depth=depth+1,
                                                           maxdepth=maxdepth))

            return delphifile

        path, filename = os.path.split(filepath)
        abspath = os.path.abspath(path)
        searchpath = []
        stdlibpath = DelphiCompiler.get_stdlibpath(relative_to=(path or '.'))

        finder_dispatch = {
            FileTypes.DelphiProjectGroup: findProjects,
            FileTypes.DelphiProject: group(findMainSource, findDelphiCompilerFlags),
            FileTypes.Program:      group(findUses, findIncludes, findResources),
            FileTypes.Library:      group(findUses, findIncludes, findResources),
            FileTypes.Package:      group(findContains, findIncludes, findResources),
            FileTypes.Unit:         group(findUses, findIncludes, findResources),
            FileTypes.FileInclude:  group(findUses, findIncludes, findResources),
        }
        if projview:
            finder_dispatch = {
                FileTypes.DelphiProjectGroup: findProjects,
                FileTypes.DelphiProject: findMainSource,
            }

        # change cwd to where the file is so that no matter what . is at
        # runtime the paths of files in the graph will be constant
        oldcwd = os.getcwd()
        try:
            io.safechdir(path)
            self.index_clear()
            df = trace_deps(filename, searchpath, stdlibpath, {}, maxdepth=maxdepth)
        finally:
            io.safechdir(oldcwd)

        return DelphiGraph(df, abspath, searchpath, stdlibpath)

    def trace_write(self, *args, **kw):
        noclobber = util.readkw(kw, 'noclobber', None)

        delphigraph = self.trace(*args, **kw)
        fp = delphigraph.to_file(noclobber=noclobber)
        return fp


if __name__ == '__main__':
    file = sys.argv[1]
    tracer = DepTracer()
    fp = tracer.trace_write(file)

    dg = DelphiGraph.from_file(fp)

    if '-d' in sys.argv:
        prettyprinter.pp(dg, collapse_duplicates=True)
        sys.exit()
    if '-s' in sys.argv:
        dotgenerator.DotGenerator(dg).show_dot()
