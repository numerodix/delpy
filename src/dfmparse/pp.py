# Copyright: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

import pprint
import re


def is_an_instance(obj):
    return hasattr(obj, '__dict__')

def get_object_id(obj):
    m = re.search('0x[0-9a-zA-Z]+', repr(obj))
    if m:
        return m.group()
    return ''

def get_class_name(obj):
    clsname = obj.__class__.__name__
    objid = get_object_id(obj)
    return '<%s {%s}>' % (clsname, objid)

def dump(obj):
    def rec(obj, visited):
        """Needs to detect instances to make sure their references don't make up a
        cycle"""
        if is_an_instance(obj):
            if obj in visited:
                return 'dup %s' % get_class_name(obj)
            visited[obj] = None

        cls = obj.__class__

        # iterable object?
        if hasattr(obj, '__iter__'):

            # label with class name if not standard collection type
            wrapdct = {}
            if cls not in [dict, list, tuple, set, frozenset]:
                wrapdct['__class'] = get_class_name(obj)

            result = None

            # dict-y?
            if hasattr(obj, 'keys') and obj.keys(): # if no keys do iter
                dct = {}
                for key in obj.keys():
                    dct[key] = rec(obj[key], visited)
                result = dct

            # list-y?
            else:
                result = cls([rec(item, visited) for item in obj])

            if wrapdct:
                wrapdct['items'] = result
                return wrapdct
            return result

        # non-iterable
        else:
            # has a repr?
            if not re.search('object at', repr(obj)):
                return repr(obj)

            else:
                # find attributes that are not functions
                atts = filter(lambda x: re.match('(?!^__)', x), dir(obj))
                atts = filter(lambda x: not hasattr(getattr(obj, x), '__call__'), atts)
                if atts:
                    dct = {}
                    dct['__class'] = get_class_name(obj)
                    for att in atts:
                        dct[att] = rec(getattr(obj, att), visited)
                    return dct
                return get_class_name(obj)

    return rec(obj, {})

def pp(st):
    # dump made general enough to handle ParseResults too
#   pprint.pprint(dump(st))

    if hasattr(st, 'asList'):
        pprint.pprint(st.asList())
    else:
        pprint.pprint(dump(st))
