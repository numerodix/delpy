#!/usr/bin/env python
#
# Copyright: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

if __name__ == '__main__': import __path__

from optparse import OptionParser
import os
import re
import string
import sys
import viewgraph

from delpy import io
from delpy import util
from delpy import delphiparser
from delpy import txlparser
from delpy.model import DelphiGraph, DelphiFile, FileTypes
from delpy.delphisrc.partition import transformer


def new_unit(handlers):
    trans = transformer.Transformer()

    unitname = 'SocketServiceHandlers'
    tree = trans.mk_unit(unitname)

    trans.listify_ast(tree)

    uses = ['SysUtils', 'Classes',
            'IdTCPConnection', 'SocketServer', 'SocketMarshall', 'SocketTypes', 'Core']
    trans.add_uses(tree, uses)

    t = trans.mk_type_spec('TServiceHandlerIndex')
    vardecl = trans.mk_var_decl(['HandlerIndex'], t)
    trans.add_var_decl(tree, vardecl)

    for handler in handlers:
        trans.add_func(tree, handler)

    delphiparser.write_file(unitname+'.pas', tree)

def trans_unit(filepath):
    tree = delphiparser.read_file(filepath)

    trans = transformer.Transformer()
    trans.listify_ast(tree)
#    trans.resolve(tree)
#    sys.exit()
    handlers = trans.remote(tree)

    trans.add_uses(tree, ['SocketClient', 'SocketMarshall', 'SocketTypes'])

    delphiparser.write_file(filepath, tree)
    return handlers




def parse_file(filepath):
    tree = delphiparser.read_file(filepath)
    trans = transformer.Transformer()
    trans.listify_ast(tree)
    return tree

def resolve_symbols_in_file(filepath):
    io.write_next_action('Resolve symbols in %s' % os.path.basename(filepath))

    tree = parse_file(filepath)

    trans = transformer.Transformer()
    symbols = trans.resolve_symbols_in_unit(tree)

    return symbols

def resolve_symbols_with_deps(abspath, symbols, df, deps):
    for dep in deps:
        fp = os.path.join(abspath, dep.path, dep.filename)
        tree = parse_file(fp)
        trans = transformer.Transformer()
        print symbols
        print trans.find_exported_symbols_in_file(tree)

def do_resolve_symbols(abspath, df, deps, cache=None):
    if not cache:
        cache = {}
    if df in cache:
        return
    cache[df] = None

    deps = filter(DelphiFile.NodePredicates.is_delphi_code, deps)

    if DelphiFile.NodePredicates.is_delphi_code(df):
        fp = os.path.join(abspath, df.path, df.filename)
        # ignore program files
        if df.filetype == FileTypes.Unit:
            unresolved = resolve_symbols_in_file(fp)
            if unresolved:
                resolve_symbols_with_deps(abspath, unresolved, df, deps)

    for dep in deps:
        do_resolve_symbols(abspath, dep, dep.nodes, cache)

def do(filepath):
    dg = viewgraph.get_graph(filepath)
    df = dg.rootnode

    df.filter_nodes(DelphiFile.NodePredicates.path_not_in(dg.stdlibpath))

    do_resolve_symbols(dg.abspath, df, df.nodes)

def main(filepath):
    do(filepath)
    return
    handlers = trans_unit(filepath)
    new_unit(handlers)


if __name__ == '__main__':
    fp = sys.argv[1]
    main(fp)
