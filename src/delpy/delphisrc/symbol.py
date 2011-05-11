#!/usr/bin/env python
#
# Copyright: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

if __name__ == '__main__': import __path__

from delpy import util
from delpy.delphisrc import unparser


class Symbol(object):
    def __init__(self, id):
        self.id = id
        self.ref = None

class QualifiedSymbol(object):
    def __init__(self, *syms):
        self.elems = syms

    @classmethod
    def new(cls, qid):
        elems = qid.split('.')
        if len(elems) > 1:
            syms = map(Symbol, elems)
            return QualifiedSymbol(*syms)
        return Symbol(qid)


class VarSymbol(object):
    def __init__(self, id, type):
        self.id = id
        self.type = type.copy()

class ConstSymbol(object):
    def __init__(self, id, value):
        self.id = id
        self.value = value.copy()
        self.type = None # XXX infer

class TypeSymbol(object):
    def __init__(self, id, value):
        self.id = id
        self.value = value.copy()

class ParamSymbol(object):
    def __init__(self, qualifier, id, type):
        if not qualifier:
            qualifier = None
        self.qualifier = qualifier
        self.id = id
        self.type = type.copy()

class FuncSymbol(object):
    def __init__(self, id, type, params):
        self.id = id
        self.type = None
        if type:
            self.type = type.copy()
        self.params = params

class ClsMemberSymbol(object):
    def __init__(self, id, ref):
        self.id = id
        self.ref = ref

class ClsSymbol(object):
    def __init__(self, id):
        self.id = id
        self.members = []

class UnitSymbol(object):
    def __init__(self, id):
        self.id = id
