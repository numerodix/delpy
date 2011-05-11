#!/usr/bin/env python
#
# Copyright: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

if __name__ == '__main__': import __path__

import copy
import os
import re
import string
import sys

from delpy import compilertools
from delpy import dotgenerator
from delpy import txlparser
from delpy import util
from delpy.model import FileTypes, DelphiFile, DelphiGraph, NodePredicates


class Node(object):
    "Baseclass for AST classes"
    def __init__(self, *a):
        for arg in a:
            self.validate_child(arg)

        self.set_children(*a)
        self.parent = None

    @classmethod
    def validate_child(cls, child):
        typ = type(child)
        if not ((typ in cls.valid_children) or
                (issubclass(typ, basestring) and
                 basestring in cls.valid_children)):
            raise Exception('Invalid nesting of %s -> %s' %
                            (cls.__name__, typ.__name__))

    @classmethod
    def extend_valid_children(cls, *children):
        cls.valid_children.extend(list(children))

    @classmethod
    def set_valid_children(cls, *children):
        cls.valid_children = list(children)

    def set_children(self, *a):
        for arg in a:
            self.validate_child(arg)

        self.children = list(a)
        for child in self.children:
            try:
                child.parent = self
            except AttributeError: pass

    def get_children_of(self, childtype):
        lst = []
        for child in self.children:
            if type(child) == childtype:
                lst.append(child)
        return lst

    def prepend_child(self, child):
        self.validate_child(child)

        self.children.insert(0, child)
        child.parent = self

    def append_child(self, child):
        self.validate_child(child)

        self.children.append(child)
        child.parent = self

    def replace_with(self, *a):
        childlst = self.parent.children[:]
        idx = childlst.index(self)
        childlst[idx:idx+1] = list(a)
        self.parent.set_children(*childlst)

    def copy(self):
        parent = self.parent
        try:
            self.parent = None
            dupe = copy.deepcopy(self)
            return dupe
        finally:
            self.parent = parent

    def unlink(self):
        self.parent.children.remove(self)
        self.parent = None

def count_nodes(node):
    count = 1
    for child in node.children:
        count += count_nodes(child)
    return count


class nodes(object):
    "Container for AST classes"
    @classmethod
    def get_nodes(cls):
        lst = []
        objnames = dir(nodes)
        for objname in objnames:
            obj = getattr(nodes, objname, None)
            try:
                if issubclass(obj, Node):
                    lst.append( (objname, obj) )
            except TypeError: pass
        return lst

    @classmethod
    def bind_names_in_scope(cls, scopedct):
        for key, val in cls.get_nodes():
            scopedct[key] = val

    @classmethod
    def get_class(cls, name):
        try:
            return getattr(cls, name)
        except AttributeError:
            return getattr(cls, ASTCreator.toCamelCase(name))


class ASTCreator(object):
    initialized = False

    node_prefixes = ['list', 'opt', 'repeat']

    node_builtins = {
        'charlit': [basestring],
        'comment': [basestring],
        'hexnumber': [basestring],
        'id': [basestring],
        'integernumber': [basestring],
        'literal': [basestring],
        'number': [basestring],

        'lit__at': [basestring],
        'repeat_lit__at': ['literal', basestring],
    }

    # pseudo nodes for traversal
    node_pseudo = ['Any', 'Many']

    @classmethod
    def capitalize(cls, s):
        s = string.capwords(s, sep='_')
        return s

    @classmethod
    def toCamelCase(cls, s):
        s = cls.capitalize(s)
        s = s.replace('_', '')
        return s

    @classmethod
    def make_class(cls, name, childnames, literals=None):
        def register_class(name):
            try:
                cl = nodes.get_class(name)
            except AttributeError:
                name_cc = cls.toCamelCase(name)
                cl = type.__new__(type, name_cc, (Node,), {})
                cl.valid_children = []
                setattr(nodes, name_cc, cl)
            return cl

        cl = register_class(name)
        children = []
        for name in childnames:
            children.append( register_class(name) )
        if literals:
            children.append(basestring)

        cl.valid_children.extend(children)
        cl.valid_children = util.uniq(cl.valid_children)

    @classmethod
    def get_txl_grammars(cls):
        txlprog = txlparser.TXLParser.grammar
        grammar_path = compilertools.DelphiCompiler.get_txl_grammar_path()
        fp_txlprog = os.path.join(grammar_path, txlprog)
        
        s = open(fp_txlprog).read()

        grammars = [txlprog]
        grammars.extend(re.findall('include "(.*?)"', s))
        grammars = map(lambda fp: os.path.join(grammar_path, fp), grammars)
        return grammars

    @classmethod
    def parse_txl_define_block(cls, block):
        rx_id = '[a-zA-Z_]+'
        rx_lit = "'[^\s\[\]]+"

        rx =  '(?s)'
        rx += '^(?:re)?define (%s)' % rx_id
        rx += '(.*)'
        rx += 'end (?:re)?define$'
        m = re.match(rx, block)
        blockname = m.group(1)
        content = m.group(2)

        # standard ids
        whitespace_ids = ['NL', 'SP', 'SPON', 'SPOFF', 'IN', 'EX']

        ids = re.findall('[[](%s)[]]' % rx_id, content)
        ids = filter(lambda id: id not in whitespace_ids, ids)

        # combinators
        prefixes = []
        prefixes_rx = '|'.join(cls.node_prefixes)
        prefixed = re.findall('[[](%s) (%s)(?:[+])?[]]' % (prefixes_rx, rx_id), content)
        for pair in prefixed:
            joined = '_'.join(pair)
            prefixes.append( (joined, pair[1]) )
            ids.append(joined)

        def get_literal_name(lit):
            if lit.startswith("'@"):
                return 'lit__at'
            else:
                return 'literal'

        # combinator literals
        prefixes_rx = '|'.join(cls.node_prefixes)
        prefixed = re.findall('[[](%s) (%s)(?:[+])?[]]' % (prefixes_rx, rx_lit), content)
        for pair in prefixed:
            comb, lit = pair
            lit = get_literal_name(lit)
            joined = comb + '_' + lit
            ids.append(joined)
            prefixes.append( (joined, lit) )

        # literals
        content = re.sub('[[].*?[]]', '', content)
        literals = re.findall(rx_lit, content)
        ids.extend(map(get_literal_name, literals))

        return blockname, ids, literals, prefixes

    @classmethod
    def register_txl_nodes(cls):
        grammars = cls.get_txl_grammars()
        for fp in grammars:
            s = open(fp).read()

            # strip comments
            s = re.sub('%.*', '', s)
            s = re.sub('#.*', '', s)

            block_rx = '(?s)(define|redefine).*?end \\1'
            for m in re.finditer(block_rx, s):
                m = m.group(0)
                name, ids, lits, prefs = cls.parse_txl_define_block(m)
                cls.make_class(name, ids, literals=lits)
                for prefixed, stem in prefs:
                    cls.make_class(prefixed, [stem])

        return nodes

    @classmethod
    def init_ast(cls):
        if cls.initialized:
            return

        # init nodes extracted from grammar
        lst = cls.register_txl_nodes()

        # init builtin nodes
        for (name, children) in cls.node_builtins.items():
            lits = False
            if basestring in children:
                children.remove(basestring)
                lits = True

            cls.make_class(name, children, literals=lits)

        # init pseudo nodes
        for name in cls.node_pseudo:
            cls.make_class(name, [])

        cls.initialized = True

ASTCreator.init_ast()

if __name__ == '__main__':
    if '-s' in sys.argv:
        root = sys.argv[2]
        terminators = sys.argv[3:]

        def build_graph(node, cache):
            if node in cache:
                return
            cache[node] = None

            df = DelphiFile(node.__name__, True, FileTypes.Unit)
            for child in getattr(node, 'valid_children', []):
                import copy
                cf = build_graph(child, copy.copy(cache))
                if cf:
                    df.add_node(cf)
            return df

        rootnode = nodes.get_class(root)
        df = build_graph(rootnode, {})

        def cut_leaves(node, children):
            if node.filename in terminators:
                node.nodes = []
        df.walk(cut_leaves)

        print('%s nodes' % len(df.collect_nodes(NodePredicates.true)))

        dg = DelphiGraph(df, '', [], [])
        dotgenerator.DotGenerator(dg).show_dot(tred=False)
    else:
        objs = nodes.get_nodes()
        for (objname,obj) in objs:
            names = map(lambda c: c.__name__, obj.valid_children)
            print('%s: [%s]' % (objname, ', '.join(names)))
        print('%s nodes' % len(objs))
