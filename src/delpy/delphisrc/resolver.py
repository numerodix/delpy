#!/usr/bin/env python
#
# Copyright: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

if __name__ == '__main__': import __path__

from delpy import util

from delpy.delphisrc import ast
from delpy.delphisrc import finder
from delpy.delphisrc import unparser

class Resolver(object):
    def __init__(self):
        ast.nodes.bind_names_in_scope(globals())


    def presolution(self, name, index):
        print '>>>>>>', name
        for (k, v) in sorted(index.items()):
            print "%-60.60s%s" % (k, v.__name__)


    def resolve_symbols_in_unit(self, node):
        scope_intf = self.find_by_type(node, InterfaceSection)[0]
        implsyms = self.find_symbols_in_unit_scope(scope_intf)
        print implsyms
#        return

        scope_impl = self.find_by_type(node, ImplementationSection)[0]
        implsyms = self.find_symbols_in_unit_scope(scope_impl)
        print implsyms

        ns = self.find_funcs_in_unit(scope_impl)
        for n in ns:
            id, func = n
            print self.find_symbols_in_func(func)
#            index = self.resolve_symbols_in_func(func, implsyms, unitsyms)

    '''
    def Zresolve_symbols_in_unit(self, node):
        scope_impl = self.find_by_type(node, ImplementationSection)[0]
        implsyms = self.find_symbols_in_unit(scope_impl)

        scope_intf = self.find_by_type(node, InterfaceSection)[0]
        unitsyms = self.find_symbols_in_unit(scope_intf)

        unresolved = []
        def update_unresolved(unresolved, index):
            for (k, v) in index.items():
                if v == Scope.Unresolved:
                    unresolved.append(k)
            return unresolved

        # Handle functions
        ns = self.find_funcs_in_unit(scope_impl)
        for n in ns:
            id, func = n
            index = self.resolve_symbols_in_func(func, implsyms, unitsyms)
            unresolved = update_unresolved(unresolved, index)
            self.presolution(id, index)

        # Handle unit level
        for scope in [InitializationSection, FinalizationSection]:
            scope= self.find_by_type(node, scope)
            if scope:
                scope = scope[0]
                index = self.resolve_symbols_in_scope(scope, implsyms, unitsyms)
                unresolved = update_unresolved(unresolved, index)
                self.presolution(type(scope).__name__, index)

        return util.iuniq(unresolved)
    '''

    def resolve_symbols_in_scope(self, node, implsyms, unitsyms):
        symbols = self.find(node, [Many, StatementList, Many, QualifiedId])
        symbols = map(self.find_str, symbols)
        symbols = util.iuniq(symbols)

        args = [symbols, None, None] \
                + [[],[],[],[],] + list(implsyms) + list(unitsyms)
        index = Scope.resolve(*args)

        return index

    def resolve_symbols_in_func(self, node, implsyms, unitsyms):
        assert(type(node) == ProcedureImplDecl)
        func = node

        cls = None
        if func:
            cls = self.func_is_a_method(func)

        symbols, localsyms = self.find_symbols_in_func(func)

        args = [symbols, func, cls] \
                + list(localsyms) + list(implsyms) + list(unitsyms)
        index = Scope.resolve(*args)

        return index
