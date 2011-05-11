#!/usr/bin/env python
#
# Copyright: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

if __name__ == '__main__': import __path__

from delpy import util
from delpy.delphisrc import ast
from delpy.delphisrc import unparser
from delpy.delphisrc.symbol import *

class Finder(object):
    def __init__(self):
        ast.nodes.bind_names_in_scope(globals())


    def mksym_symbol(self, v):
        sym = QualifiedSymbol.new(v)
        return sym

    def mksym_var(self, v):
        id, typespec = v
        sym = VarSymbol(self.find_str(id), typespec)
        return sym

    def mksym_const(self, v):
        id, value = v
        sym = ConstSymbol(self.find_str(id), value)
        return sym

    def mksym_type(self, v):
        id, value = v
        sym = TypeSymbol(self.find_str(id), value)
        return sym

    def mksym_param(self, v):
        qual, id, typespec = v
        sym = ParamSymbol(self.find_str(qual), self.find_str(id), typespec)
        return sym

    def mksym_func(self, v):
        id = self.find_funcname_in_func(v)
        typespec = self.find_functype_in_func(v)
        params = map(self.mksym_param, self.find_params_in_func(v))
        sym = FuncSymbol(self.find_str(id), typespec, params)
        return sym

    def mksym_class(self, v):
        id, cls = v
        sym = ClsSymbol(id)
        members = []

        ms = self.find_methods_in_class(cls)
        for m in ms:
            mid, t = m
            funcsym = self.mksym_func(t)
            memsym = ClsMemberSymbol(mid, funcsym)
            members.append(memsym)

        vs = self.find_variables_in_class(cls)
        for v in vs:
            vid, ts = v
            varsym = self.mksym_var(v)
            memsym = ClsMemberSymbol(vid, varsym)
            members.append(varsym)

        # XXX handle as variable
        ps = self.find_properties_in_class(cls)
        for p in ps:
            pid, _,  ts, _, _ = p
            varsym = self.mksym_var((pid,ts))
            memsym = ClsMemberSymbol(vid, varsym)
            members.append(varsym)

        sym.members = members
        return sym

    def mksym_unit(self, v):
        id = v
        sym = UnitSymbol(self.find_str(id))
        return sym


    def find_symbols_in_func(self, node):
        assert(type(node) == ProcedureImplDecl)

        params = []
        ts = self.find_params_in_func(node)
        for t in ts:
            params.append(self.mksym_param(t))

        consts = []
        ts = self.find_consts_in_func(node)
        for t in ts:
            consts.append(self.mksym_const(t))

        types = []
        ts = self.find_types_in_func(node)
        for t in ts:
            types.append(self.mksym_type(t))

        vars = []
        ts = self.find_vars_in_func(node)
        for t in ts:
            vars.append(self.mksym_var(t))

        symbols = self.find(node, [Many, ProcedureBodySemi, Many, QualifiedId])
        symbols = map(self.find_str, symbols)
        symbols = util.iuniq(symbols)
        symbols = map(self.mksym_symbol, symbols)

        return symbols, (params, consts, types, vars)

    def find_symbols_in_unit_scope(self, node):
        assert(type(node) in [InterfaceSection, ImplementationSection])

        uses = []
        ts = self.find_uses_in_unit(node)
        for t in ts:
            uses.append(self.mksym_unit(t))

        # XXX classes
        classes = []
        clsnames = []
        ts = self.find_classes_in_unit(node)
        for t in ts:
            cid, _ = t
            clsnames.append(cid)
            classes.append(self.mksym_class(t))

        consts = []
        ts = self.find_consts_in_unit(node)
        for t in ts:
            consts.append(self.mksym_const(t))

        types = []
        ts = self.find_types_in_unit(node)
        for t in ts:
            tid, _ = t
            if self.find_str(tid) not in clsnames:
                types.append(self.mksym_type(t))

        vars = []
        ts = self.find_vars_in_unit(node)
        for t in ts:
            vars.append(self.mksym_var(t))

        funcs = []
        ts = self.find_funcs_in_unit(node)
        for t in ts:
            id, f = t
            funcs.append(self.mksym_func(f))

        return uses, classes, consts, types, vars, funcs

    '''
    def find_exported_symbols_in_file(self, node):
        assert(type(node) == Program)
        intf = self.find(node, [Many, InterfaceSection])[0]

        classes, consts, types, vars, funcs = \
                self.find_symbols_in_unit(intf)
        return classes + consts + types + vars + funcs
    '''
