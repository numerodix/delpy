#!/usr/bin/env python
#
# Copyright: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

if __name__ == '__main__': import __path__

from delpy import util
from delpy.delphisrc import ast
from delpy.delphisrc import astpp
from delpy.delphisrc import constructor
from delpy.delphisrc import finder
from delpy.delphisrc import resolver
from delpy.delphisrc import unparser

class Transformer(constructor.Constructor,
                  finder.Finder,
                  resolver.Resolver):
    def __init__(self):
        constructor.Constructor.__init__(self)
        finder.Finder.__init__(self)
        resolver.Resolver.__init__(self)
        ast.nodes.bind_names_in_scope(globals())


    def listify(self, node, parent, children, path_to, localpaths):
        unparser.Unparser.override(parent)
        parent.extend_valid_children(*children)

        trees = self.find(node, path_to, rec=True)
        for tree in trees:
            lst = []
            for path in localpaths:
                lst.extend(self.find(tree, path))

            tree.set_children(*lst)

        # XXX clashes with multiple file parsing, successive file parsed
        # against changed grammar
#        parent.set_valid_children(*children)

    def listify_identlists(self, node):
        path_to = [
            Many,
            Identlist,
        ]
        localpaths = [
            [
                Any,
                Id,
            ],
            [
                Any,
                RepeatCommaId,
                CommaId,
                Id,
            ]
        ]
        self.listify(node, Identlist, [Id], path_to, localpaths)

    def listify_set(self, node):
        path_to = [
            Many,
            SetConstructor,
        ]
        localpaths = [
            [
                Any,
                BoxSetElement,
                OptSetElement,
                SetElement,
            ],
            [
                Any,
                ManyCommaSetElement,
                RepeatCommaSetElement,
                CommaSetElement,
                SetElement,
            ]
        ]
        self.listify(node, SetConstructor, [SetElement], path_to, localpaths)

    def listify_params(self, node):
        path_to = [
            Many,
            FormalParameters,
        ]
        localpaths = [
            [
                Any,
                FormalParameter,
            ],
            [
                Any,
                RepeatSemiFormalParameter,
                SemiFormalParameter,
                FormalParameter,
            ]
        ]
        self.listify(node, FormalParameters, [FormalParameter], path_to, localpaths)

    def listify_argms(self, node):
        path_to = [
            Many,
            Arguments,
        ]
        localpaths = [
            [
                Any,
                OptArgm,
                Argm,
            ],
            [
                Any,
                RepeatCommaArgm,
                CommaArgm,
                Argm,
            ]
        ]
        self.listify(node, Arguments, [Argm], path_to, localpaths)

    def listify_stmlist(self, node):
        path_to = [
            Many,
            StatementList,
        ]
        localpaths = [
            [
                Any,
                ManyStatementSemi,
                RepeatStatementSemi,
                StatementSemi,
            ],
            [
                Any,
                BoxStatement,
                OptStatement,
                Statement,
            ]
        ]
        self.listify(node, StatementList, [StatementSemi, Statement], path_to, localpaths)

    def listify_ast(self, node):
        self.listify_identlists(node)
        self.listify_set(node)
        self.listify_params(node)
        self.listify_argms(node)
        self.listify_stmlist(node)


    def add_uses(self, unit, args):
        path = [
            Many,
            UnitFile,
            InterfaceSection,
            BoxUsesClause,
        ]
        tree = self.find(unit, path)[0]

        path = [
            Any,
            OptUsesClause,
            UsesClause,
            ListUsesItem,
            UsesItem,
        ]
        items = self.find(tree, path)
        lst = map(lambda i: self.find_string(i), items)
        lst.extend(args)
        lst = util.iuniq(lst)

        uses_clause = self.mk_uses_clause(*lst)
        box = OptUsesClause(uses_clause)
        tree.set_children(box)

    def add_var_decl(self, unit, var_decl):
        path = [
            Many,
            UnitFile,
            InterfaceSection,
            IntfdeclBlock,
        ]
        rep = self.find_probe(unit, path, RepeatIntfdeclSection)

        t = IntfdeclSection(self.mk_var_section(var_decl))
        rep.append_child(t)

    def add_func(self, unit, func):
        # Add body to impl
        path = [
            Many,
            UnitFile,
            ImplementationSection,
            ImpldeclBlock,
        ]
        rep = self.find_probe(unit, path, RepeatImpldeclSection)

        t = ImpldeclSection(func)
        rep.append_child(t)

        # Add signature to impl
        func_sig = self.find_by_type(func, ProcedureIntfDecl)[0]

        path = [
            Many,
            UnitFile,
            InterfaceSection,
            IntfdeclBlock,
        ]
        rep = self.find_probe(unit, path, RepeatIntfdeclSection)

        t = IntfdeclSection(func_sig)
        rep.append_child(t)
