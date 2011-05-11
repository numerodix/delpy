#!/usr/bin/env python
#
# Copyright: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

if __name__ == '__main__': import __path__

from delpy import util
from delpy.delphisrc.scope import Scope


class SymbolTable(object):
    def __init__(self):
        self.index = {}

    def set(self, unitid, blockid, symbol):
        if unitid not in self.index:
            self.index[unitid] = {}

        if blockid not in self.index[unitid]:
            self.index[unitid][blockid] = {}

        self.index[unitid][blockid][symbol.id] = symbol



st = SymbolTable()
sym = Symbol('price', 'integer', Scope.LocalVar)
fsym = Symbol('Effe', 'integer', Scope.UnitFunc)
st.set('Gui', 'TFormMain.BtnCheckPriceClick', sym)
st.set('Gui', 'InterfaceSection', fsym)
from delpy.lib import prettyprinter as pp
pp.pp(st)
