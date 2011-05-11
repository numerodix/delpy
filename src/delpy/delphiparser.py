#!/usr/bin/env python
#
# Copyright: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

if __name__ == '__main__': import __path__

from optparse import OptionParser
import os
import re
import sys
import xml.dom.minidom
import xml.etree.cElementTree as etree

from delpy import compilertools
from delpy import io
from delpy import txlparser
from delpy.delphisrc import ast
from delpy.delphisrc import astpp
from delpy.delphisrc import transformer
from delpy.delphisrc import unparser

__all__ = ['read_file', 'output_tree', 'output_code', 'write_file']

# XXX workaround for LangUtils.pas
sys.setrecursionlimit(15000)

class XMLReader(object):
    def get_class(self, name):
        name = str(name)
        cl = ast.nodes.get_class(name)
        return cl()

    def patch_input(self, s):
        s = s.replace('<repeat_lit__@>', '<repeat_lit__at>')
        s = s.replace('</repeat_lit__@>', '</repeat_lit__at>')
        return s

    def reify_minidom(self, st):
        if st.nodeName == '#text':
            return st.nodeValue.strip()

        child_objs = []
        for child in st.childNodes:
            if not re.match('^\s+$', child.nodeValue or ''):
                child_obj = self.reify_minidom(child)
                child_objs.append( child_obj )

        obj = self.get_class(st.nodeName)
        obj.set_children(*child_objs)
        return obj

    def reify_etree(self, node):
        if isinstance(node, basestring):
            return node

        child_objs = []

        if node.text:
            value = node.text.strip()
            if value:
                child_objs.append(value)

        for child in node.getchildren():
            child_obj = self.reify_etree(child)
            child_objs.append(child_obj)
            tail = child.tail
            if tail:
                tail = tail.strip()
                if tail:
                    tail_obj = self.reify_etree(tail)
                    child_objs.append(tail_obj)

        obj = self.get_class(node.tag)
        obj.set_children(*child_objs)
        return obj

    def get_tree_etree(self, xml_str):
        try:
            try:
                doc = etree.fromstring(xml_str)
            except SyntaxError:
                input_codec = compilertools.DelphiCompiler.get_dcc_charset()
                xml_str = xml_str.decode(input_codec).encode("utf-8")
                doc = etree.fromstring(xml_str)
        except SyntaxError:
            xml_str = self.patch_input(xml_str)
            doc = etree.fromstring(xml_str)
        tree = self.reify_etree(doc)
        return tree

    def get_tree_minidom(self, xml_str):
        try:
            try:
                doc = xml.dom.minidom.parseString(xml_str)
            except xml.parsers.expat.ExpatError:
                input_codec = compilertools.DelphiCompiler.get_dcc_charset()
                xml_str = xml_str.decode(input_codec).encode("utf-8")
                doc = xml.dom.minidom.parseString(xml_str)
        except xml.parsers.expat.ExpatError:
            xml_str = self.patch_input(xml_str)
            doc = xml.dom.minidom.parseString(xml_str)
        rootnode = doc.childNodes[0]
        tree = self.reify_minidom(rootnode)
        return tree


def read_file(filepath, use_minidom=False):
    xml_str = txlparser.parse_file(filepath)

    if use_minidom:
        tree = XMLReader().get_tree_minidom(xml_str)
    else:
        tree = XMLReader().get_tree_etree(xml_str)

    return tree

def output_tree(tree):
    tree_fmt = astpp.sprint(tree)
    codec = compilertools.DelphiCompiler.get_dcc_charset()
    tree_fmt = tree_fmt.encode(codec)
    io.output(tree_fmt)

def output_code(tree):
    code = unparser.unparse(tree)
    io.output(code)

def write_file(filepath, tree):
    code = unparser.unparse(tree)
    open(filepath, 'w').write(code)


def process_file(filepath, print_tree=False, unparse=True, use_minidom=False):
    tree = read_file(filepath, use_minidom=use_minidom)

    if print_tree:
        trans = transformer.Transformer()
        trans.listify_ast(tree)
        output_tree(tree)
        return

    if unparse:
        write_file(filepath, tree)
    else:
        output_code(tree)

def main(filepath, *a, **kw):
    filelist = txlparser.get_file_list(filepath)

    interactive = True
    if os.path.isdir(filepath):
        interactive = False
        kw['unparse'] = True

    def write(msg):
        if not interactive:
            io.output(msg)

    failures = 0
    for fp in filelist:
        success = True
        try:
            process_file(fp, *a, **kw)
        except:
            success = False
            if interactive:
                raise

        lab = "SUCCEEDED"
        if not success:
            failures += 1
            lab = "FAILED"
        localname = io.relpath(fp, relative_to=filepath)
        localname = localname == "." and filepath or localname
        write("%-9.9s  %s\n" % (lab.upper(), localname))
    write("Processed %s files, %s failed\n" % (len(filelist), failures))

    exitcode = failures > 0 and 1 or 0
    return exitcode


if __name__ == '__main__':
    usage = "%s  <path>" % sys.argv[0]
    optparser = OptionParser(usage=usage)
    optparser.add_option("-u", "--unparse", dest="unparse", action="store_true",
                         help="Unparse tree")
    optparser.add_option("-t", "--tree", dest="print_tree", action="store_true",
                         help="Display syntax tree")
    optparser.add_option("", "--minidom", dest="use_minidom", action="store_true",
                         help="Use minidom over etree (slower)")
    (options, args) = optparser.parse_args()

    try:
        filepath = args[0]
    except IndexError:
        optparser.print_help()
        sys.exit(1)

    exitcode = main(filepath,
                    print_tree=options.print_tree,
                    unparse=options.unparse,
                    use_minidom=options.use_minidom)
    sys.exit(exitcode)
