#!/usr/bin/env python
#
# Copyright: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

if __name__ == '__main__': import __path__

from delpy import util
from delpy.delphisrc import ast
from delpy.delphisrc import unparser

class Finder(object):
    def __init__(self):
        ast.nodes.bind_names_in_scope(globals())


    def find_uses_in_unit(self, node):
        assert(type(node) in [InterfaceSection, ImplementationSection])
        path = [
            Any,
            BoxUsesClause,
            OptUsesClause,
            UsesClause,
            ListUsesItem,
            UsesItem,
            QualifiedId,
        ]
        ns = self.find(node, path)
        return ns


    def find_classes_in_unit(self, node):
        assert(type(node) in [InterfaceSection, ImplementationSection])
        ns = self.find_types_in_unit(node)
        lst = []
        for (id, typespec) in ns:
            ts = self.find_classes(typespec)
            if ts:
                id = self.find_classname_in_class(ts[0])
                lst.append( (id, ts[0]) )
        return lst

    def find_records_in_unit(self, node):
        assert(type(node) in [InterfaceSection, ImplementationSection])
        ns = self.find_types_in_unit(node)
        lst = []
        for (id, typespec) in ns:
            ts = self.find_records(typespec)
            if ts:
                id = self.find_classname_in_class(ts[0])
                lst.append( (id, ts[0]) )
        return lst

    def find_funcs_in_unit(self, node):
        assert(type(node) in [InterfaceSection, ImplementationSection])
        path = [
            Any,
            Any,
            Any,
            Any,
            Any,
        ]
        ns = self.find(node, path)
        ns = filter(lambda n: type(n) in [ProcedureImplDecl,
                                          ProcedureIntfDecl], ns)
        lst = []
        for n in ns:
            id = self.find_funcname_in_func(n)
            lst.append( (id, n) )
        return lst


    def find_consts_in_unit(self, node):
        assert(type(node) in [InterfaceSection, ImplementationSection])
        path = [
            Any,
            Any,
            Any,
            Any,
            ConstSection,
            Any,
            ConstantDecl,
        ]
        ns = self.find(node, path)
        ns = map(self.select_in_const_decl, ns)
        ns = util.flatten(ns)
        return ns

    def find_types_in_unit(self, node):
        assert(type(node) in [InterfaceSection, ImplementationSection])
        path = [
            Any,
            Any,
            Any,
            Any,
            TypeSection,
            Any,
            TypeDecl,
        ]
        ns = self.find(node, path)
        ns = map(self.select_in_type_decl, ns)
        ns = util.flatten(ns)
        return ns

    def find_vars_in_unit(self, node):
        assert(type(node) in [InterfaceSection, ImplementationSection])
        path = [
            Any,
            Any,
            Any,
            Any,
            VarSection,
            Any,
            VarDecl,
        ]
        ns = self.find(node, path)
        ns = map(self.select_in_var_decl, ns)
        ns = util.flatten(ns)
        return ns
