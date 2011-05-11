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


    def stm_is_in_funcbody(self, node):
        assert(type(node) in [StatementSemi, Statement])
        ns = self.findup(node, ProcedureImplDecl)
        return ns

    def func_is_a_method(self, node):
        assert(type(node) in [ProcedureImplDecl, ProcedureIntfDecl])
        fn = self.find_funcname_in_func(node)
        elems = fn.split('.')
        if len(elems) == 2:
            clsname, funcname = elems
            return clsname


    def find_funcname_in_func(self, node):
        assert(type(node) in [ProcedureImplDecl, ProcedureIntfDecl])
        path = [
            Many,
            ProcedureIntfDecl,
            ProcedureSignature,
            Many,
            ProcedureId,
        ]
        n = self.find(node, path)[0]
        n = self.find_str(n)
        return n

    def find_params_in_func(self, node):
        assert(type(node) in [ProcedureImplDecl, ProcedureIntfDecl])
        path = [
            Many,
            ProcedureIntfDecl,
            ProcedureSignature,
            Many,
            FormalParameters,
            FormalParameter,
        ]
        ns = self.find(node, path)
        ns = map(self.select_in_formal_parameter, ns)
        ns = util.flatten(ns)
        return ns

    def find_functype_in_func(self, node):
        assert(type(node) in [ProcedureImplDecl, ProcedureIntfDecl])
        path = [
            Many,
            ProcedureIntfDecl,
            ProcedureSignature,
            BoxColonType,
            Any,
            ColonType,
            TypeSpec,
        ]
        ns = self.find(node, path)
        if ns:
            return ns[0]

    def find_consts_in_func(self, node):
        assert(type(node) == ProcedureImplDecl)
        path = [
            Many,
            NestedDeclBlock,
            Many,
            ConstSection,
            Any,
            ConstantDecl,
        ]
        ns = self.find(node, path)
        ns = map(self.select_in_const_decl, ns)
        ns = util.flatten(ns)
        return ns

    def find_types_in_func(self, node):
        assert(type(node) == ProcedureImplDecl)
        path = [
            Many,
            NestedDeclBlock,
            Many,
            TypeSection,
            Any,
            TypeDecl,
        ]
        ns = self.find(node, path)
        ns = map(self.select_in_type_decl, ns)
        ns = util.flatten(ns)
        return ns

    def find_vars_in_func(self, node):
        assert(type(node) == ProcedureImplDecl)
        path = [
            Many,
            NestedDeclBlock,
            Many,
            VarSection,
            Any,
            VarDecl,
        ]
        ns = self.find(node, path)
        ns = map(self.select_in_var_decl, ns)
        ns = util.flatten(ns)
        return ns
