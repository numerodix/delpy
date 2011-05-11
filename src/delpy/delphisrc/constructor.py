#!/usr/bin/env python
#
# Copyright: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

if __name__ == '__main__': import __path__

import re

from delpy.delphisrc import ast
from delpy.delphisrc import consexpr, consfunc, consstm, constype, consunit, consvar

class Constructor(consexpr.Constructor,
                  consfunc.Constructor,
                  consstm.Constructor,
                  constype.Constructor,
                  consunit.Constructor,
                  consvar.Constructor):
    def __init__(self):
        consexpr.Constructor.__init__(self)
        consfunc.Constructor.__init__(self)
        consstm.Constructor.__init__(self)
        constype.Constructor.__init__(self)
        consunit.Constructor.__init__(self)
        consvar.Constructor.__init__(self)
        ast.nodes.bind_names_in_scope(globals())

    def p(self, x):
        import astpp
        import unparser
        try:
            print 'a>', astpp.sprint(x).strip()
            print 'c>', unparser.unparse(x)
        except: print x
        print

    def ps(self, xs):
        for x in xs:
            self.p(x)

    def unp(self, x):
        import unparser
        zs = [x]
        if hasattr(x, '__iter__'):
            zs = x
        xs = []
        for z in zs:
            if hasattr(z, '__iter__'):
                xs.extend(z)
            else:
                xs.append(z)

        for x in xs:
            try:
                print 'c>', unparser.unparse(x)
            except: print x
            print


    def mk_commentlist(self, s):
        return Commentlist(OptManyComments(
                ManyComments(RepeatAnycomment(
                        Anycomment(Commentline(Comment(s)))))))

    def mk_char_lit(self, s):
        return Charlit("'" + s + "'")

    def mk_namespace(self, id):
        return Namespace(Id(id, '.'))

    def mk_qualified_id(self, *args):
        args = list(args)
        if len(args) == 1:
            args = args[0].split('.')

        arg_last = args.pop()
        heads = map(lambda s: self.mk_namespace(s), args)
        if heads:
            heads = RepeatNamespace(*heads)
        last = Name(Id(arg_last))

        qid = QualifiedId(last)
        if heads:
            qid = QualifiedId(heads, last)
        return qid
