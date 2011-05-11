#!/usr/bin/env python
#
# Copyright: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

if __name__ == '__main__': import __path__


class ASTPrinter(object):
    nl = "\n"
    tablen = 2
    linewidth = 78

    @classmethod
    def get_tabs(cls, indent):
        return (indent*cls.tablen)*" "

    @classmethod
    def format_inline(cls, triple):
        (opener, items, closer) = triple
        body = ", ".join(items)
        fmt = "".join([opener, body, closer])
        return fmt

    @classmethod
    def format_block(cls, triple, indent):
        (opener, items, closer) = triple

        tabs = cls.get_tabs(indent)
        fmt = opener
        for (i, item) in enumerate(items):
            delim = "  "
            if i != 0:
                delim = ", "
            fmt += cls.nl + tabs + delim + item
        fmt += cls.nl + tabs + closer

        return fmt

    @classmethod
    def format(cls, node, indent=0):
        if isinstance(node, basestring):
            return '"%s"' % node

        items = []
        for child in node.children:
            items.append( cls.format(child, indent=indent+1) )

        tabs = cls.get_tabs(indent)

        triple = (
            node.__class__.__name__ + "(",
            items,
            ")"
        )
        node_s = cls.format_inline(triple)
        if len(tabs + node_s) > cls.linewidth:
            node_s = cls.format_block(triple, indent)

        return node_s

    @classmethod
    def sprint(cls, node):
        s = cls.format(node)
        s += "\n"
        return s


def sprint(node):
    return ASTPrinter.sprint(node)
