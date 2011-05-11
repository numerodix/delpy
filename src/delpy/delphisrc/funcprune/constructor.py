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

    def mk_visibility_block_empty(self, visiblity_kw):
        t = VisibilityBlock(
            Visibility(
                Commentlist(),
                VisibilityKw(visiblity_kw)
            ),
            ManyClassMember(RepeatClassMember()))
        return t

    def mk_vardecl(self, id, typespec):
        t = VarDecl(
            Commentlist(),
            Identlist(Id(id)),
            ColonType(
                Colon(":"),
                typespec),
            BoxHintDirective(),
            BoxVarInit(),
            BoxSemi(OptLiteral(Literal(";")))
        )
        return t

    def mk_writeln(self, msg):
        stm = StatementSemi(StatementSemiComp(BoxStatement(OptStatement(
            Statement(
                Commentlist(),
                UnlabeledStm(CallStm(Expr(Expression(Term(
                    Commentlist(),
                    AtomExpr(QualifiedId(Name(Id("WriteLn")))),
                    RepeatPostfixOpr(PostfixOpr(
                        Arguments("(", 
                                  OptArgm(Argm(Commentlist(),
                                               Expression(Term(
                                                   Commentlist(),
                                                   AtomExpr(Charlit("'%s'" % msg)))))),
                                  ")"))))))))))),
            Commentlist(),
            ";"))
        return stm

    def mk_funcbody_empty_sequence_stm(self):
        stm = SequenceStm(
            Commentlist(),
            BeginKw("begin"),
            StatementList(
                ManyStatementSemi(),
                BoxStatement()
            ),
            EndKw(Commentlist(), "end;")
        )
        return stm

    def mk_sequence_stm(self, *children):
        stm = SequenceStm(
            Commentlist(),
            BeginKw("begin"),
            StatementList(
                *children
            ),
            EndKw(Commentlist(), "end")
        )
        return stm
