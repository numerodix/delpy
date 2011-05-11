# Copyright: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

if __name__ == '__main__': import __path__

import re
import sys


def safeindex(lst, idx, val):
    try:
        return lst[idx]
    except IndexError:
        return val

def readkw(dct, key, default):
    try:
        v = dct.pop(key)
    except KeyError:
        v = default
    return v

def longest(lst):
    if not lst:
        return 0
    return max(map(len, lst))

def match_lists(lst1, lst2, itemget):
    dct1, dct2 = {}, {}
    for item in lst1:
        dct1[itemget(item)] = item
    for item in lst2:
        dct2[itemget(item)] = item
    keys = uniq(dct1.keys() + dct2.keys())
    lst = []
    for key in keys:
        v1 = dct1.get(key)
        v2 = dct2.get(key)
        if v1 and v2:
            lst.append((v1, v2))
    return lst

def flatten(lst):
    newlst = []
    for sublst in lst:
        for elem in sublst:
            newlst.append(elem)
    return newlst

def uniq(lst):
    """Order preserving unique-ifier"""
    dct = {}
    new_lst = []
    for elem in lst:
        if elem not in dct:
            dct[elem] = None
            new_lst.append(elem)
    return new_lst

def iuniq(lst):
    """Order preserving unique-ifier"""
    dct = {}
    new_lst = []
    for elem in lst:
        if elem.lower() not in dct:
            dct[elem.lower()] = None
            new_lst.append(elem)
    return new_lst

def isort(lst):
    return sorted(lst, cmp=lambda x,y: cmp(x.lower(), y.lower()))

def setminus(lst1, lst2):
    """Order preserving set subtraction"""
    nlst = []
    for elem in lst1:
        if elem not in lst2:
            nlst.append(elem)
    return nlst

def filteron(rx, lst):
    """Filter string list on regex"""
    return filter(lambda f: re.match(rx, f), lst)

def find_module_funcs_matching(modname, rx):
    funcs = dir(sys.modules[modname])
    funcs = sorted(map(lambda s: re.sub(rx,'',s), filteron(rx, funcs)))
    funcs_s = ', '.join(funcs)
    return funcs_s
