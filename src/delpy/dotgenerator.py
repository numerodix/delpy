# Copyright: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

if __name__ == '__main__': import __path__

import os
import re

from delpy import compilertools
from delpy import io
from delpy.model import FileTypes


class DotGenerator(object):
    def __init__(self, delphigraph):
        self.delphigraph = delphigraph
        self.delphifile = self.delphigraph.rootnode

    def get_dot_name(self, delphifile):
        """Make name valid as dot node"""
        name = delphifile.filename
        return re.sub('(?i)[^a-z0-9]', '_', name)

    def get_label_name(self, delphifile, nodename):
        """Type dependent node labeling"""
        label = '"%s"' % delphifile.filename
        if delphifile.filetype in (FileTypes.Unit, FileTypes.CompiledUnit):
            name, _ = os.path.splitext(delphifile.filename)
            label = '"%s"' % name
        return label

    def style_node(self, delphifile):
        nodename = self.get_dot_name(delphifile)
        atts = {}
        atts['shape'] = 'box'
        atts['style'] = 'filled'
        atts['label'] = self.get_label_name(delphifile, nodename)
        if delphifile.filetype == FileTypes.Unit:
            atts['fillcolor'] = 'bisque1'
        elif delphifile.filetype == FileTypes.CompiledUnit:
            atts['fillcolor'] = 'bisque3'
        elif delphifile.filetype == FileTypes.Program:
            atts['shape'] = 'ellipse'
            atts['fillcolor'] = 'firebrick1'
        elif delphifile.filetype == FileTypes.Library:
            atts['shape'] = 'ellipse'
            atts['fillcolor'] = 'darkorange'
        elif delphifile.filetype == FileTypes.Package:
            atts['shape'] = 'ellipse'
            atts['fillcolor'] = 'darkorchid1'
        elif delphifile.filetype in (FileTypes.Resource, FileTypes.Form):
            atts['shape'] = 'note'
            atts['fillcolor'] = 'aquamarine'
        if not delphifile.exists:
            atts['fontcolor'] = 'red'
        atts_s = ','.join([k + '=' + v for (k,v) in atts.items()])
        atts_s = '%s [%s];\n' % (nodename, atts_s)
        return atts_s

    def style_edge(self, start, end):
        dot_s = ''
        if start.path != end.path:
            rel = io.relpath(end.path, start.path)
            dot_s = ' [label="%s"]' % rel
        return dot_s

    def gen_dot(self):
        graph = []
        nodedefs = {}

        def f(delphifile, children):
            if delphifile.filename not in nodedefs:
                nodestyle = self.style_node(delphifile)
                if nodestyle:
                    nodedefs[delphifile.filename] = nodestyle

            for child in children:
                name_src = self.get_dot_name(delphifile)
                name_target = self.get_dot_name(child)

                # XXX labeling edges with path makes the picture rather messsy
                #styling = self.style_edge(delphifile, child)
                styling = ''

                graph.append('  %s -> %s%s;' % (name_src, name_target, styling))

        self.delphifile.walk(f)
        graph_dot = '\n'.join(graph)

        nodedefs_dot = ''
        for k in sorted(nodedefs.keys()):
            nodedefs_dot += '  %s' % nodedefs[k]
        dot_code = 'digraph %s {\n%s%s}\n' % (self.get_dot_name(self.delphifile),
                                              graph_dot, nodedefs_dot)
        return dot_code

    def write_dot(self, path, file_src):
        dot_code = self.gen_dot()
        open(os.path.join(path, file_src), 'w').write(dot_code)

    def compile_dot(self, tmpdir, file_src, file_target, format,
                   transitive_reduction=True, unflatten=True):
        """ tred: computes transitive reduction, meaning if App.dpr imports Lib.pas and
        Module.pas, and Module.pas itself imports Lib.pas, the edge from App.dpr to
        Lib.pas is eliminated
        """
        (dotbin, tredbin, unflattenbin) = io.find_dot_tools()
        if transitive_reduction:
            ret, output = io.invoke([tredbin, file_src], cwd=tmpdir)
            if not ret:
                open(os.path.join(tmpdir, file_src), 'w').write(output)
        if unflatten:
            ret, output = io.invoke([unflattenbin, file_src], cwd=tmpdir)
            if not ret:
                open(os.path.join(tmpdir, file_src), 'w').write(output)
        io.invoke([dotbin, '-T%s' % format, file_src, '-o', file_target], cwd=tmpdir)

    def show_dot(self, tred=True):
        format = 'pdf'
        file_src = io.get_tmpfile(self.delphifile.filename)
        file_target = io.get_tmpfile('%s.%s' % (self.delphifile.filename, format))

        # split up
        tmpdir = os.path.dirname(file_src)
        file_src = os.path.basename(file_src)
        file_target = os.path.basename(file_target)

        self.write_dot(tmpdir, file_src)

        self.compile_dot(tmpdir, file_src, file_target, format,
                         transitive_reduction=tred)

        try:
            reader = io.find_pdf_reader()
            io.invoke([reader, file_target], cwd=tmpdir)
        except:
            import traceback
            traceback.print_exc()
        finally:
            os.unlink(os.path.join(tmpdir, file_src))
            os.unlink(os.path.join(tmpdir, file_target))
