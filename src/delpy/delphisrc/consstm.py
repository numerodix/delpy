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

    def mk_func_call(self, qualified_id, *args):
        def mk_argm(term):
            t = Argm(Commentlist(), Expression(term))
            return t

        def mk_arguments(*a):
            return RepeatPostfixOpr(PostfixOpr(Arguments(*a)))

        fname = AtomExpr(qualified_id)
        items = [Commentlist(), fname]

        if args:
            args = map(mk_argm, args)
            fargs = mk_arguments(*args)
            items.append(fargs)

        t = Expression(Term(*items))
        return t

    def mk_call_stm(self, func_call):
        return CallStm(Expr(func_call))

    def mk_assign_stm(self, qualified_id, expression):
        var = Expr(
            Expression(
                Term(
                    Commentlist(),
                    AtomExpr(qualified_id)
                )))
        t = AssignStm(var, ':=', Expr(expression))
        return t

    def mk_if_stm(self, pred, *stms):
        block = self.mk_statement_block(*stms)
        t = SelectionStm(
            IfStm(
                'if',
                Expr(pred),
                'then',
                NestedStm(block),
                BoxElseStm()
            )
        )
        return t

    def mk_statement_semi(self, stm, comment=None):
        commentlist = Commentlist()
        if comment:
            commentlist = comment
        t = StatementSemi(
            StatementSemiComp(
                BoxStatement(
                    OptStatement(
                        Statement(
                            commentlist,
                            UnlabeledStm(stm)
                        )
                    )
                ),
                Commentlist(),
                ';'
        ))
        return t

    def mk_statement_block(self, *args):
        t = SequenceStm(
            Commentlist(),
            BeginKw('begin'),
            StatementList(*args),
            EndKw(
                Commentlist(),
                'end'
            )
        )
        return t
