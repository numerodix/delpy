#!/usr/bin/env python
#
# Copyright: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

if __name__ == '__main__': import __path__

from delpy.delphisrc import ast
from delpy.delphisrc import finder
from delpy.delphisrc import unparser

class Finder(finder.Finder):
    def __init__(self):
        super(self.__class__, self).__init__()
        ast.nodes.bind_names_in_scope(globals())

    def get_class_name(self, node):
        path = [
            Many,
            TypeDecl,
            Identlist,
            Id,
            basestring,
        ]
        name = self.get(node, path)[0]
        return name

    def get_visibility_kw(self, node):
        path = [
            VisibilityBlock,
            Visibility,
            VisibilityKw,
            Many,
            basestring,
        ]
        lst = self.get(node, path)
        if lst:
            return lst[0]

    def get_property_name(self, node):
        path = [
            PropertyDecl,
            PropId,
            Id,
            basestring,
        ]
        namelst = self.get(node, path)
        if namelst:
            return namelst[0]

    def get_property_func_name(self, node):
        path = [
            Many,
            Id,
            basestring,
        ]
        namelst = self.get(node, path)
        if namelst:
            return namelst[0]

    def get_func_name(self, node):
        path = [
            Many,
            ProcedureSignature,
            Many,
            ProcedureId,
            Many,
            Id,
            basestring,
        ]
        elems = self.get(node, path)
        name = ".".join(elems)
        return name

    def get_type_spec(self, node):
        path = [
            Many,
            TypeSpec,
        ]
        lst = self.get(node, path)
        if lst:
            return lst[0]

    def get_func_sig_s(self, node):
        path = [
            Many,
            ProcedureSignature,
        ]
        sigs = self.get(node, path)
        if sigs:
            sig = sigs[0]
            cls, kw, id, params, typespec = sig.children
            name = self.get_func_name(node)
            params = unparser.unparse(params)
            type = unparser.unparse(typespec)
            return "".join([name, params, type])
