# Copyright: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

if __name__ == '__main__': import __path__

import cPickle as pickle
import os

from delpy import io
from delpy import util

class Serializable(object):
    serialize_extension = '.graph'

    def to_file(self, noclobber=None):
        filename = self.get_serialized_name()
        filepath = io.get_tmpfile('%s%s' % (filename,
                                            self.serialize_extension),
                                 noclobber=noclobber)

        flatobj = self.get_serialized_obj()

        # XXX use older pickle format for mixing with different python versions
#        pickle.dump(flatobj, open(filepath, 'wb'), pickle.HIGHEST_PROTOCOL)
        # open to write as binary to preempt win/lin portability bug
        pickle.dump(flatobj, open(filepath, 'wb'))

        io.write_result("Wrote file %s ." % filepath)
        return filepath

    @classmethod
    def from_file(self, filepath):
        st = pickle.load(open(filepath))

        obj = self.get_deserialized_obj(st)

#        io.write_result("Loaded file %s ." % filepath)
        return obj


class Diff(object):
    def __init__(self, name):
        self.name = name
        self.atts = {}

    def add_att(self, k, v):
        self.atts[k] = v

    def keys(self):
        return self.atts.keys()

    def iteritems(self):
        keys = sorted(self.atts.keys())
        for key in keys:
            yield key, self.atts[key]

class Diffable(object):
    def diff(self, other):
        fmt = lambda x: x.diffname() if hasattr(x, 'diffname') else x

        atts = util.uniq(self.__dict__.keys() + other.__dict__.keys())
        dct = {}
        for att in atts:
            my_attobj = fmt(getattr(self, att, None))
            other_attobj = fmt(getattr(other, att, None))
            if my_attobj != other_attobj:
                # if is iterable try to use diffname()
                if hasattr(my_attobj, '__iter__'):
                    my_attobj = map(fmt, my_attobj)
                if hasattr(other_attobj, '__iter__'):
                    other_attobj = map(fmt, other_attobj)

                dct[att] = (my_attobj, other_attobj)
        if dct:
            diffobj = Diff(self.diffname())
            for (k, v) in dct.items():
                diffobj.add_att(k, v)
            return diffobj
