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

    def mk_type_spec(self, id):
        qid = self.mk_qualified_id(id)
        t = TypeSpec(
            Commentlist(),
            TypeSpecInner(qid)
        )
        return t

    def mk_type_spec_simple(self, tname):
        t = TypeSpec(
            Commentlist(),
            TypeSpecInner(SimpleType(OrdinalType(IntegerType(tname))))
        )
        return t

    def mk_colon_type(self, typespec):
        return ColonType(Colon(':'), typespec)
