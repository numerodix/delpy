#!/usr/bin/env python
#
# Copyright: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

if __name__ == '__main__': import __path__

from delpy.delphisrc import ast
from delpy.delphisrc import unparser

class Finder(object):
    def __init__(self):
        ast.nodes.bind_names_in_scope(globals())


    def select_in_formal_parameter(self, node):
        assert(type(node) == FormalParameter)
        c, qual, parameter = node.children
        idlist, opttype = parameter.children
        typespec = self.find_by_type(opttype, TypeSpec)[0]
        lst = []
        for id in idlist.children:
            lst.append( (qual, id, typespec) )
        return lst

    def select_in_const_decl(self, node):
        assert(type(node) == ConstantDecl)
        c, idlist, constspec, hintdir, semi = node.children
        eq, expr = constspec.children[0].children
        lst = []
        for id in idlist.children:
            lst.append( (id, expr) )
        return lst

    def select_in_type_decl(self, node):
        assert(type(node) == TypeDecl)
        c, idlist, eq, boxtype, typespec, hintdir, semi = node.children
        lst = []
        for id in idlist.children:
            lst.append( (id, typespec) )
        return lst

    def select_in_var_decl(self, node):
        assert(type(node) == VarDecl)
        c, idlist, colontype, hintdir, varinit, semi = node.children
        colon, typespec = colontype.children
        lst = []
        for id in idlist.children:
            lst.append( (id, typespec) )
        return lst

    def select_in_property_decl(self, node):
        assert(type(node) == PropertyDecl)
        kw, id, indexes, boxcoltype, manypropspec, boxarrayspec, semi = node.children

        typespec = None
        t = self.find_by_type(boxcoltype, ColonType)
        if t:
            typespec = t[0]

        return id, indexes, typespec, manypropspec, boxarrayspec
