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

    def mk_identlist(self, *args):
        ids = map(Id, args)
        return Identlist(*ids)

    def mk_var_decl(self, ids, typespec):
        identlist = self.mk_identlist(*ids)
        colon_type = self.mk_colon_type(typespec)

        t = VarDecl(
            Commentlist(),
            identlist,
            colon_type,
            BoxHintDirective(),
            BoxVarInit(),
            BoxSemi(OptLiteral(Literal(";")))
        )
        return t

    def mk_var_section(self, *args):
        t = VarSection(
            Commentlist(),
            VarKeyword("var"),
            RepeatVarDecl(*args)
        )
        return t
