#!/usr/bin/env python
#
# Copyright: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

if __name__ == '__main__': import __path__

from delpy import util

from delpy.delphisrc import ast
from delpy.delphisrc import unparser
from delpy.delphisrc import findclass, findfunc, findselect, findsymbol, findunit

class Finder(findclass.Finder,
             findfunc.Finder,
             findselect.Finder,
             findsymbol.Finder,
             findunit.Finder):
    def __init__(self):
        findclass.Finder.__init__(self)
        findfunc.Finder.__init__(self)
        findselect.Finder.__init__(self)
        findsymbol.Finder.__init__(self)
        findunit.Finder.__init__(self)
        ast.nodes.bind_names_in_scope(globals())


    def find(self, node, path, rec=False):
        if rec == True:
            rec = path[:]

        acc = []

        pathcopy = path[:]

        if pathcopy:
            pathelem = pathcopy.pop(0)

            recurse = False

            if issubclass(type(node), pathelem) or pathelem == Any:
                path = pathcopy

                if not pathcopy:
                    acc.append(node)
                    if rec:
                        path = rec[:]
                        recurse = True
                else:
                    recurse = True

            elif pathelem == Many:
                if pathcopy:
                    pathelem = pathcopy.pop(0)

                    if issubclass(type(node), pathelem):
                        if not pathcopy:
                            acc.append(node)
                            if rec:
                                path = rec[:]
                                recurse = True
                        else:
                            path = pathcopy
                            recurse = True
                    else:
                        recurse = True

            if recurse:
                for child in getattr(node, 'children', []):
                    acc.extend( self.find(child, path, rec=rec) )

        return acc

    def findup(self, node, nodetype):
        needle = None
        while not needle and hasattr(node, 'parent'):
            node = node.parent
            if type(node) == nodetype:
                return node

    def findup_get(self, node, nodetype, path):
        nodes = []
        node = self.findup(node, nodetype)
        if node:
            nodes = self.find(node, path)
        return nodes

    def find_probe(self, node, path, nestedcls):
        tree = self.find(node, path)[0]

        nested = self.find_by_type(tree, nestedcls)
        if nested:
            nested = nested[0]
        else:
            nested = nestedcls()
            tree.set_children(nested)
        return nested

    def find_by_type(self, node, nodetype):
        path = [
            Many,
            nodetype,
        ]
        return self.find(node, path)

    def find_str(self, node):
        path = [
            Many,
            basestring,
        ]
        elems = self.find(node, path)
        name = ''.join(elems)
        return name

    def find_string(self, node):
        path = [
            Many,
            Id,
            basestring,
        ]
        elems = self.find(node, path)
        name = ".".join(elems)
        return name

    def find_assign_stm_operands(self, node):
        lvalue, sign, rvalue = node.children
        variable = self.find_by_type(lvalue, QualifiedId)[0]
        path = [
            Expr,
            Expression,
            Term,
        ]
        term = self.find(rvalue, path)[0]
        return variable, term

    def find_func_call_args(self, node):
        path = [
            Many,
            Arguments,
            Argm,
        ]
        return self.find(node, path)

    def find_comment_matching(self, node, needle):
        path = [
            Many,
            Commentlist,
            OptManyComments,
            ManyComments,
            RepeatAnycomment,
            Anycomment,
            Commentline,
            Comment,
        ]
        found = []
        trees = self.find(node, path, rec=True)
        for tree in trees:
            path = [
                Comment,
                basestring,
            ]
            t = self.find(tree, path)
            if t:
                if t[0] == needle:
                    n = tree.parent.parent.parent.parent.parent.parent.parent
                    found.append(n)

        return found
