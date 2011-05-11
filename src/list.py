#!/usr/bin/env python
#
# Copyright: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.
#
# <desc>
# Lists tools with their descriptions.
# </desc>

import os
import re
import sys


fnmatch = '(?i)^.*\.py$'

field = '(?ims)# <desc>.*?</desc>'

def green(s):
    if (not os.environ.get("TERM")) or (os.environ.get("TERM") == "dumb"):
        return s
    return '\033[32m%s\033[0m' % s

def main():
    collected = []
    for (root, dirs, files) in os.walk('.'):
        for file in files:
            if re.match(fnmatch, file):
                fp = os.path.join(root, file)
                if re.search(field, open(fp).read()):
                    collected.append(fp)

    collected = sorted(collected)
    for fp in collected:
        content = open(fp).read()
        m = re.search(field, content)
        if m:
            print(green('== %s ==' % fp))
            desc = m.group(0)
            # kill tags
            desc = re.sub('(?i)[<][^>]*[>]', '', desc)
            # kill comments
            desc = re.sub('#', '', desc)
            # kill leading space
#            desc = '\n'.join(map(lambda s: re.sub('^\s*', '', s),
#                                 desc.splitlines()))
            # kill whitespace lines
            desc = '\n'.join(filter(lambda s: not re.match('^\s*$', s),
                                    desc.splitlines()))
            print desc


if __name__ == '__main__':
    main()
