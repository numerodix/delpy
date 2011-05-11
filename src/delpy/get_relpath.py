#!/usr/bin/env python
#
# Copyright: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

if __name__ == '__main__': import __path__

import os
import sys

from delpy import io


if __name__ == '__main__':
    try:
        (frm, to) = sys.argv[1:3]
    except IndexError:
        print("Usage:  %s <from_path> <to_path>" % sys.argv[0])
    print(io.relpath(to, relative_to=frm))
