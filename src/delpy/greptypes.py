#!/usr/bin/env python
#
# Copyright: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

if __name__ == '__main__': import __path__

import os
import re
import sys

from delpy import io
from delpy import finders

def find_types(fp):
    iden = '[a-zA-Z]+(\.[a-zA-Z]+)*'    # namespaced
    rx = '(?P<subtype>%s)' % iden
    rx += '\s+=\s+'
    rx += 'class\s*'
    rx += '([(](?P<supertype>%s)[)])?' % iden
    s = open(fp).read()
    s = finders.find_stripComments(s)
    fp = os.path.basename(fp)
    (stem, _) = os.path.splitext(fp)
    for m in re.finditer(rx, s):
        subtype = m.group('subtype')
        supertype = m.group('supertype') or 'TObject'
        subtype = '%s.%s' % (stem, subtype)
        print("%-50.50s: %s" % (subtype, supertype))


if __name__ == '__main__':
    codebase = sys.argv[1]
    units = io.ifind(codebase, '*.pas')
    units.extend(io.ifind(codebase, '*.dpr'))
    for unit in units:
        find_types(unit)
