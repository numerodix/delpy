#!/usr/bin/env python
#
# Copyright: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

if __name__ == '__main__': import __path__

from delpy import util


class LocalScope(object): pass
class ObjectScope(object): pass
class ImplScope(object): pass
class IntfScope(object): pass


'''
class Scope(object):
    @classmethod
    def derive(cls, name):
        cl = type.__new__(type, name, (cls,), {})
        setattr(cls, name, cl)

    @classmethod
    def get_scopes(cls):
        lst = []
        keys = dir(cls)
        for key in keys:
            obj = getattr(cls, key, None)
            try:
                if issubclass(obj, cls):
                    lst.append( (key, obj) )
            except TypeError: pass
        return lst

    @classmethod
    def make_symbol_dict(cls, symbols, strip=None):
        dct = {}
        for symbol in symbols:
            elems = symbol.split('.')
            if strip and len(elems) > 1:
                if strip.lower() == elems[0].lower():
                    elems = elems[1:]

            key = elems[0].lower()
            if key not in dct:
                dct[key] = []
            if symbol not in dct[key]:
                dct[key].append(symbol)

        return dct

    @classmethod
    def make_scope_dict(cls, symbols, strip=None):
        dct = {}
        for symbol in symbols:
            if strip:
                elems = symbol.split('.')
                if len(elems) > 1 and elems[0].lower() == strip.lower():
                    symbol = '.'.join(elems[1:])

            key = symbol.lower()
            dct[key] = symbol
        return dct

    @classmethod
    def apply_scope(cls, scope, scopecls, symbols, index):
        for (k, vs) in symbols.items():
            if k in scope:
                for v in vs:
                    index[v] = scopecls
                del(symbols[k])

    @classmethod
    def resolve(cls,
                symbols,
                infunc, inclass,
                localparams, localconsts, localtypes, localvars,
                implclassmembers, implconsts, impltypes, implvars, implfuncs,
                unitclassmembers, unitconsts, unittypes, unitvars, unitfuncs
               ):
        index = {}

        symbols = cls.make_symbol_dict(symbols)

        if infunc:
            localparams = cls.make_scope_dict(localparams)
            localconsts = cls.make_scope_dict(localconsts)
            localtypes = cls.make_scope_dict(localtypes)
            localvars = cls.make_scope_dict(localvars)

            cls.apply_scope(localconsts, cls.LocalConst, symbols, index)
            cls.apply_scope(localtypes, cls.LocalType, symbols, index)
            cls.apply_scope(localvars, cls.LocalVar, symbols, index)
            cls.apply_scope(localparams, cls.LocalParam, symbols, index)

        implconsts = cls.make_scope_dict(implconsts)
        impltypes = cls.make_scope_dict(impltypes)
        implvars = cls.make_scope_dict(implvars)
        implfuncs = cls.make_scope_dict(implfuncs)

        cls.apply_scope(implconsts, cls.ImplConst, symbols, index)
        cls.apply_scope(impltypes, cls.ImplType, symbols, index)
        cls.apply_scope(implvars, cls.ImplVar, symbols, index)
        cls.apply_scope(implfuncs, cls.ImplFunc, symbols, index)

        unitconsts = cls.make_scope_dict(unitconsts)
        unittypes = cls.make_scope_dict(unittypes)
        unitvars = cls.make_scope_dict(unitvars)
        unitfuncs = cls.make_scope_dict(unitfuncs)

        cls.apply_scope(unitconsts, cls.UnitConst, symbols, index)
        cls.apply_scope(unittypes, cls.UnitType, symbols, index)
        cls.apply_scope(unitvars, cls.UnitVar, symbols, index)
        cls.apply_scope(unitfuncs, cls.UnitFunc, symbols, index)

        if inclass:
            symbols = util.flatten(symbols.values())
            symbols = cls.make_symbol_dict(symbols, strip='self')

            implclassmembers = cls.make_scope_dict(implclassmembers, strip=inclass)
            unitclassmembers = cls.make_scope_dict(unitclassmembers, strip=inclass)

            cls.apply_scope(implclassmembers, cls.ImplClassMember, symbols, index)
            cls.apply_scope(unitclassmembers, cls.UnitClassMember, symbols, index)

        for vs in symbols.values():
            for v in vs:
                index[v] = cls.Unresolved

        return index


Scope.derive('LocalParam')
Scope.derive('LocalConst')
Scope.derive('LocalType')
Scope.derive('LocalVar')

Scope.derive('ImplClassMember')
Scope.derive('ImplConst')
Scope.derive('ImplType')
Scope.derive('ImplVar')
Scope.derive('ImplFunc')

Scope.derive('UnitClassMember')
Scope.derive('UnitConst')
Scope.derive('UnitType')
Scope.derive('UnitVar')
Scope.derive('UnitFunc')

Scope.derive('FuncBody')
Scope.derive('InitBlock')
Scope.derive('FinBlock')

Scope.derive('Unresolved')


if __name__ == '__main__':
    scopes = Scope.get_scopes()
    for (name, cls) in sorted(scopes):
        print(name)
'''
