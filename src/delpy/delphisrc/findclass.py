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


    def find_filter_class_type_s(self, node, filterkw):
        path = [
            Many,
            ClassType,
        ]
        ns = self.find(node, path)
        def select(n):
            packedkw, classkw, abstract, heritage, body = n.children
            if classkw.children[0] == filterkw:
                return True
        ns = filter(select, ns)
        return ns

    def find_classes(self, node):
        ns = self.find_filter_class_type_s(node, 'class')
        return ns

    def find_records(self, node):
        ns = self.find_filter_class_type_s(node, 'record')
        return ns


    def find_classname_in_class(self, node):
        assert(type(node) == ClassType)
        ns = self.findup_get(node, TypeDecl, [Any, Identlist])
        if ns:
            return self.find_str(ns[0])

    def find_methods_in_class(self, node):
        assert(type(node) == ClassType)
        path = [
            Many,
            ClassBody,
            Many,
            ClassMember,
            Any,
            MethodDecl,
            ProcedureIntfDecl,
        ]
        ns = self.find(node, path)
        lst = []
        for n in ns:
            id = self.find_funcname_in_func(n)
            lst.append( (id, n) )
        return lst

    def find_variables_in_class(self, node):
        assert(type(node) == ClassType)
        path = [
            Many,
            ClassBody,
            Many,
            ClassMember,
            Any,
            VarDecl,
        ]
        ns = self.find(node, path)
        ns = map(self.select_in_var_decl, ns)
        ns = util.flatten(ns)
        return ns

    def find_properties_in_class(self, node):
        assert(type(node) == ClassType)
        path = [
            Many,
            ClassBody,
            Many,
            ClassMember,
            Any,
            PropertyDecl,
        ]
        ns = self.find(node, path)
        ns = map(self.select_in_property_decl, ns)
        return ns
