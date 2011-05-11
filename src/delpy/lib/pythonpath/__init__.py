import sys

# import names from system stdlib
import ntpath
import posixpath

# import names from curdir
if not (hasattr(ntpath, 'relpath') and hasattr(posixpath, 'relpath')):
    import _ntpath as ntpath
    import _posixpath as posixpath
