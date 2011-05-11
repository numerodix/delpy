# Copyright: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

if __name__ == '__main__': import __path__

import copy
import os

from delpy import util
from delpy.mixins import Serializable, Diffable


class Categories(object):
    class Category(object): pass
    class Source(Category): pass
    class Product(Category): pass
    class Cache(Category): pass

class FileTypes(object):
    '''Models the various types of files that occur in a Delphi codebase'''
    _list_of_filetypes = []     # sorted in order of significance

    _extension_map = {}     # .pas      -> Unit
    _source_name_map = {}   # library   -> Library
    _source_files = {}      # {.dpk, .dpr, .pas}
    _filetypename_map = {}      # 'Form'    -> Form
    _filetypename_revmap = {}

    class FileType(object): pass

    @classmethod
    def derive(cls, name, extension, source_name=None, category=None,
               build_target=False):
        # add dot to ease lookup
        extension = extension[0] == '.' and extension or '.'+extension

        # derive new class
        exec('class %s(cls.FileType): pass' % name)
        exec('%s.name = "%s"' % (name, name))
        exec('%s.extension = "%s"' % (name, extension))

        exec('%s.source_file = False' % name)
        if source_name:
            exec('%s.source_file = True' % name)
            exec('%s.source_name = "%s"' % (name, source_name))
            exec('cls._source_name_map["%s"] = %s' % (source_name, name))
            exec('cls._source_files["%s"] = None' % (extension))

        # assign filetype category
        if category:
            exec('%s.category = Categories.%s' % (name, category.__name__))

        exec('%s.build_target = False' % name)
        if build_target:
            exec('%s.build_target = True' % name)

        # assign to container class
        exec('cls.%s = %s' % (name, name))

        # add to list of filetypes
        exec('cls._list_of_filetypes.append(%s)' % name)

        # add to index
        # an extension can map to more than one filetype, make it a list
        exec(('if not "%s" in cls._extension_map:' +
                'cls._extension_map["%s"] = []') % (extension, extension))
        exec('cls._extension_map["%s"].append(%s)' % (extension, name))

        # add to filetypename map
        exec('cls._filetypename_map["%s"] = cls.%s' % (name, name))
        exec('cls._filetypename_revmap[cls.%s] = "%s"' % (name, name))

    @classmethod
    def is_source_file(cls, filename):
        stem, ext = os.path.splitext(filename)
        ext = ext.lower()
        return ext in cls._source_files

    @classmethod
    def get_filetype_from_source_name(cls, source_name):
        return cls._source_name_map[source_name]

    @classmethod
    def get_filetypes_from_extension(cls, filename):
        stem, ext = os.path.splitext(filename)
        ext = ext.lower()
        filetype = cls._extension_map.get(ext)
        if not filetype:
            filetype = [cls.Unknown]
        return filetype

    @classmethod
    def get_filetype_from_filetypename(cls, filetypename):
        return cls._filetypename_map[filetypename]

    @classmethod
    def get_filetypename_from_filetype(cls, filetypeobj):
        return cls._filetypename_revmap[filetypeobj]

    @classmethod
    def get_filetypes_by_category(cls, match_category):
        return filter(lambda t: getattr(t, 'category', None) == match_category,
                      cls._list_of_filetypes)

    @classmethod
    def get_filetypes_by_build_target(cls):
        return filter(lambda t: t.build_target, cls._list_of_filetypes)

# instantiate by most significant first
_der = FileTypes.derive
_Src = Categories.Source
_Pro = Categories.Product
_Cac = Categories.Cache
# sources
_der('DelphiProjectGroup', 'bdsgroup', category=_Src, build_target=True)
_der('DelphiProject', 'bdsproj', category=_Src, build_target=True)
_der('DelphiCompilerFlags', 'cfg', category=_Src)
_der('Program', 'dpr', source_name='program', category=_Src, build_target=True)
_der('Library', 'dpr', source_name='library', category=_Src, build_target=True)
_der('Package', 'dpk', source_name='package', category=_Src, build_target=True)
_der('Unit', 'pas', source_name='unit', category=_Src)
_der('Form', 'dfm', category=_Src)
_der('Resource', 'res', category=_Src)
_der('FileInclude', 'inc', source_name='include', category=_Src)
_der('Unknown', '*')
# products
_der('CompiledProgram', 'exe', category=_Pro)
_der('CompiledLibrary', 'dll', category=_Pro)
_der('CompiledPackage', 'bpl', category=_Pro) # without flags
_der('CompiledPackage', 'dcp', category=_Pro) # with some compiler flag
_der('CompiledControlPanel', 'cpl', category=_Pro)
_der('CompiledActiveXControl', 'ocx', category=_Pro)
_der('CompiledUnit', 'dcu', category=_Pro)
_der('BinaryObject', 'obj', category=_Pro)
# cache files
_der('DelphiProjectCache', 'local', category=_Cac)
_der('DelphiProjectIdentcache', 'identcache', category=_Cac)


class FileIndex(object):
    """Mix in class to handle file indexing"""
    def __init__(self):
        self.index_clear()

    def index_clear(self):
        self._index = {}

    def _prepare_path(self, filepath):
        '''Filepaths are hashed by filepath,
        but special case hashing is done for units (.pas or .dcu), in
        accordance with the concept of a search path (ie. the same filename
        in a different location is still the same unit. Thus hashing of units
        is by filename.'''
        filepath = filepath.lower()
#        filepath = os.path.basename(filepath)
        stem, ext = os.path.splitext(filepath)
        if ext in ['.pas', '.dcu']:
            filepath = os.path.basename(filepath)
        return filepath

    def index_has(self, filepath):
        fileobj = self.index_get(filepath)
        return fileobj and True or False

    def index_get(self, filepath):
        filename = self._prepare_path(filepath)
        fileobj = self._index.get(filename)
        if not fileobj:
            stem, ext = os.path.splitext(filename)
            if ext == '.pas':
                filename = stem + '.dcu'
                fileobj = self._index.get(filename)
        return fileobj

    def index_set(self, filepath, obj):
        filename = self._prepare_path(filepath)
        self._index[filename] = obj


class DelphiGraph(Serializable, Diffable):
    '''Wrap a graph of DelphiFile objects'''
    def __init__(self, rootnode, abspath, searchpath, stdlibpath):
        self.rootnode = rootnode
        self.abspath = abspath
        # XXX for some inexplicable reason the searchpath is duplicated
        # when tracing with explore_codebase
        self.searchpath = util.iuniq(searchpath)
        self.stdlibpath = stdlibpath
        self.index = None

    # Serialization methods

    @classmethod
    def filepath_is_graph(cls, filepath):
        _, ext = os.path.splitext(filepath)
        if ext == cls.serialize_extension:
            return True

    def get_serialized_name(self):
        return self.rootnode.filepath

    def get_serialized_obj(self):
        def rec(node, idx):
            if node.filepath.lower() in idx:
                return
            idx[node.filepath.lower()] = node

            if hasattr(node, 'nodes'):
                for (i, n) in enumerate(node.nodes):
                    node.nodes[i] = n.filepath
                    rec(n, idx)

            return idx

        idx = rec(self.rootnode, {})
        self.index = idx
        return self

    @classmethod
    def get_deserialized_obj(cls, aself):
        def rec(node, idx, cache):
            if node in cache:
                return
            cache[node] = None

            if hasattr(node, 'nodes'):
                for (i, n) in enumerate(node.nodes):
                    if not isinstance(n, DelphiFile):
                        n = idx[n.lower()]
                    node.nodes[i] = n
                    rec(n, idx, cache)
            return node

        rec(aself.rootnode, aself.index, {})
        aself.index = None
        return aself

    # Diffing methods

    @classmethod
    def diff_graphs(self, fst, snd):
        def rec(f_node, s_node, diffs, cache):
            if f_node in cache:
                return
            cache[f_node] = None

            diff = f_node.diff(s_node)
            if diff:
                diffs.append(diff)
            if (hasattr(f_node, 'nodes') and
                hasattr(s_node, 'nodes')):
                    nodes = util.match_lists(f_node.nodes, s_node.nodes,
                                             lambda o: o.diffname())
                    for (f_n, s_n) in nodes:
                        if f_n == s_n:
                            rec(f_n, s_n, diffs, cache)

        diffs = []
        diff = fst.diff(snd)
        if diff:
            diffs.append(diff)
        rec(fst.rootnode, snd.rootnode, diffs, {})
        return diffs

    # Diffing methods

    def __eq__(self, other):
        '''For diffing'''
        return self.diffname().lower() == other.diffname().lower()

    def diffname(self):
        return self.rootnode.filepath


class DelphiFile(Diffable):
    '''Represents a file in a Delphi codebase'''
    def __init__(self, filepath, exists, filetype):
        filename = os.path.basename(filepath)
        path = os.path.dirname(filepath)
        self.filename = filename
        self.path = path
        self.exists = exists
        self.filetype = filetype

    def _get_filepath(self):
        return os.path.join(self.path, self.filename)
    filepath = property(fget=_get_filepath)

    def _set_filetype(self, filetypeobj):
        self._filetype = FileTypes.get_filetypename_from_filetype(filetypeobj)

    def _get_filetype(self):
        return FileTypes.get_filetype_from_filetypename(self._filetype)

    filetype = property(fset=_set_filetype, fget=_get_filetype)

    def add_node(self, fileobj):
        if not hasattr(self, 'nodes'):
            self.nodes = []
        self.nodes.append(fileobj)

    def walk(self, func, recursive_cache=False):
        '''Walk with a function f, return nothing
        The cache is used to preempt cycles, and is global.
        recursive_cache can be used to enable a path-only cache.'''
        def rec(node, f, cache, depth=0):
            if node in cache:
                return
            cache[node] = None

            children = getattr(node, 'nodes', [])

            # XXX this is a hack
            try:
                f(node, children, depth)
            except TypeError:
                f(node, children)

            for child in children:
                rec(child, f, pre_recurse(cache), depth=depth+1)

        pre_recurse = lambda x: x
        if recursive_cache:
            # copy the dict before recursing, so it will only accumulate values
            # down a path, not globally
            pre_recurse = copy.copy

        rec(self, func, {})

    def collect_nodes(self, predicate):
        nodes = []
        def f(node, children):
            if predicate(node):
                nodes.append(node)
        self.walk(f)
        return nodes

    def filter_nodes(self, predicate):
        def f(node, children):
            node.nodes = filter(predicate, children)
        self.walk(f)

    # Diffing methods

    def __eq__(self, other):
        '''For diffing'''
        return self.diffname().lower() == other.diffname().lower()

    def diffname(self):
        return self.filepath


class NodePredicates(object):
    @staticmethod
    def true(n):
        return True

    @staticmethod
    def filename_is(filename):
        def f(n):
            return n.filename.lower() == filename.lower()
        return f

    @staticmethod
    def file_notexists(n):
        return not n.exists

    @staticmethod
    def is_delphi_code(n):
        return n.filetype in [FileTypes.Program, FileTypes.Package, FileTypes.Unit]

    @staticmethod
    def is_not_dcu(n):
        return n.filetype != FileTypes.CompiledUnit

    @staticmethod
    def is_not_obj(n):
        return n.filetype != FileTypes.BinaryObject

    @staticmethod
    def is_not_resource(n):
        return n.filetype not in (FileTypes.Resource, FileTypes.Form)

    @staticmethod
    def path_not_in(path):
        def f(n):
            return n.path not in path
        return f

DelphiFile.NodePredicates = NodePredicates


class OptionException(Exception): pass
