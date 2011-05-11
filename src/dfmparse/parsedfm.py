#!/usr/bin/env python
#
# Copyright: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.
#
# <desc>
# Parses Delphi forms (.dfm).
# </desc>

import sys

from pyparsing import *

class Widget(object): pass

def mkWidget(t):
    widget = Widget()
    widget.label = t.label
    widget.name = t.name
    if t.type:
        widget.type = t.type
    if t.list:
        widget.list = t.list
    for node in t.nodes:
        if isinstance(node, Widget):
            if not hasattr(widget, 'children'):
                widget.children = []
            widget.children.append(node)
        else:
            if not hasattr(widget, 'properties'):
                widget.properties = {}
            k, v = node
            widget.properties[k] = v
    return widget

def parse(filepath):
    literal = lambda c: Suppress(c)
    caseless_literal = lambda c: Suppress(CaselessLiteral(c))
    space = Suppress(White(ws=' '))
    whites = Suppress(OneOrMore(White(ws=' \n\r\t')))


    digits = Word(nums)
    number = Combine(
        Optional('-') 
        + digits 
        + Optional('.'
                   + digits 
                   + Optional('E' + digits)
                  )
    )

    # string: 'Don'#39't Prompt Again' + \n'rest of the string'
    string_simple = literal("'") + SkipTo("'") + literal("'")
    # XXX convert character code to unicode?
    character_code = Combine('#' + Word(nums))
    string_compund = Combine(OneOrMore(string_simple | character_code))
    string = Combine(
        string_compund
        + ZeroOrMore(
            ZeroOrMore(whites)
            + Optional('+')
            + ZeroOrMore(whites)
            + string_compund
        )
    )


    identifier = Word(alphas+'_', alphanums+'_')
    namespaced_identifier = Combine(
        identifier + ZeroOrMore('.' + identifier)
    )


    lst = Combine(
        '[' + SkipTo(']') + ']'
    )

    paren = Forward()
    paren_val = identifier | number | string | paren
    paren << Combine(
        '('
        + Optional(whites)
        + Optional(paren_val + ZeroOrMore(whites + paren_val))
        + Optional(whites)
        + ')'
    )

    # XXX parse subitems?
    angle = nestedExpr(opener='<', closer='>')

    base16_line = Word('0123456789abcdefABCDEF')
    base16 = Combine(
        literal('{')
        + Optional(whites)
        + base16_line + ZeroOrMore(whites + base16_line)
        + Optional(whites)
        + literal('}')
    )


    label = oneOf('inherited inline object', caseless=True)

    head = (
        label('label')
        + space
        + identifier('name')
        + Optional( literal(':') + identifier('type') )
        + Optional(lst)('list')
    )
    end = CaselessLiteral('end')


    pairvalue = (
        number
        | string
        | namespaced_identifier
        | lst
        | paren
        | angle
        | base16
    )

    pair = Group(
        namespaced_identifier
        + literal('=')
        + pairvalue
    )

    widget = Forward().setParseAction(mkWidget)
    widget << head + (
        ZeroOrMore(
            widget
            | pair
        )('nodes')
    ) + end

    doc = widget + stringEnd
    st = doc.parseFile(filepath).asList()

    return st


if __name__ == '__main__':
    source = sys.argv[1]
    st = parse(source)
    if '-d' in sys.argv:
        import pp
        pp.pp(st)
