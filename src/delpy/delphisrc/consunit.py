#!/usr/bin/env python
#
# Copyright: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

if __name__ == '__main__': import __path__

import re

from delpy.delphisrc import ast

class Constructor(object):
    def __init__(self):
        ast.nodes.bind_names_in_scope(globals())

    def mk_unit(self, name):
        qid = self.mk_qualified_id(name)
        t = Program(
            DelphiFile(
                UnitFile(
                    UnitDecl(
                        Commentlist(),
                        "unit",
                        qid,
                        BoxHintDirective(),
                        ";"
                    ),
                    InterfaceSection(
                        InterfaceKw(Commentlist(), "interface"),
                        BoxUsesClause(),
                        IntfdeclBlock()
                    ),
                    ImplementationSection(
                        ImplementationKw(Commentlist(), "implementation"),
                        BoxUsesClause(),
                        ImpldeclBlock()
                    ),
                    BoxInitializationSection(),
                    BoxFinalizationSection(),
                    EndKw(Commentlist(), "end"),
                    FileEnd(".")
                )
            )
        )
        return t

    def mk_uses_clause(self, *a):
        args = map(self.mk_qualified_id, a)

        def mk_uses_item(qid):
            t = UsesItem(Commentlist(), qid, BoxInFilename())
            return t
        args = map(mk_uses_item, args)

        t = UsesClause(Commentlist(), 'uses', ListUsesItem(*args), ';')
        return t
