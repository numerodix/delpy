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

    def mk_term(self, qualified_id):
        t = Term(
            Commentlist(),
            AtomExpr(qualified_id)
        )
        return t

    def mk_term_with_prefix(self, operator, qualified_id):
        t = Term(
            Commentlist(),
            RepeatPrefixOpr(PrefixOpr(operator)),
            AtomExpr(qualified_id)
        )
        return t

    def mk_infix_expr(self, operator, term):
        t = InfixExpr(
            InfixOpr(operator),
            term)
        return t

    def mk_expression_predicate(self, lvalue, operator, rvalue):
        t_left = self.mk_term(lvalue)
        rvalue = self.mk_term(rvalue)
        t_right = RepeatInfixExpr(self.mk_infix_expr(operator, rvalue))
        return Expression(t_left, t_right)

    def mk_set_constructor(self, *terms):
        elems = map(lambda t: SetElement(Expression(t)), terms)
        t = SetConstructor(*elems)
        return t
