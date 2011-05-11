#!/usr/bin/env python
#
# Copyright: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

if __name__ == '__main__': import __path__

import re
import string
import uuid

from delpy.delphisrc import ast
from delpy.delphisrc import transformer
from delpy.delphisrc import unparser
from delpy.delphisrc.funcprune import constructor
from delpy.delphisrc.funcprune import finder

class Transformer(transformer.Transformer,
                  constructor.Constructor,
                  finder.Finder):
    def __init__(self):
        transformer.Transformer.__init__(self)
        constructor.Constructor.__init__(self)
        finder.Finder.__init__(self)
        ast.nodes.bind_names_in_scope(globals())


    def prepend_writeln_in_funcbody(self, node, msg):
        path = [
            Many,
            ProcedureBody,
        ]
        procbody = self.find(node, path)
        for node in procbody:

            # standard case
            path = [
                Any,
                SequenceStm,
                StatementList,
            ]
            stmlists = self.find(node, path)
            for stmlist in stmlists:
                stm = self.mk_writeln(msg)
                stmlist.prepend_child(stm)

            # asm case
            path = [
                Any,
                AsmStmtblock,
            ]
            asmblocks = self.find(node, path)
            if asmblocks:
                stm = self.mk_writeln(msg)
                asmblocks.insert(0, stm)
                node.set_children(self.mk_sequence_stm(*asmblocks))
    
    def inject_writeln(self, node):
        path = [
            Many,
            ImpldeclSection,
            ProcedureImplDecl,
            ProcedureIntfDecl,
        ]
        nodes = self.find(node, path)

        pairs = []
        index = FuncIndex()
        for node in nodes:
            funcname = self.find_funcname_in_func(node)
            index.inc(funcname)
            funcname = index.get_labeled(funcname)

            s = uuid.uuid4()
            pairs.append( (s, funcname) )
            self.prepend_writeln_in_funcbody(node.parent, s)

        return pairs


    def remove_funcsig_classlevel(self, node, funcnames_by_class):
        kept, removed = [], []

        path = [
            Many,
            TypeDecl,
        ]
        nodes = self.find(node, path)
        for node in nodes:
            clsname = self.find_class_name(node)
            if clsname and clsname.lower() in funcnames_by_class:

                ## Find methods bound in properties

                kept_methods = []
                path = [
                    Many,
                    ClassType,
                    Many,
                    ClassBody,
                    Many,
                    RepeatClassMember,
                    ClassMember,
                    ClassMemberInner,
                    PropertyDecl,
                    ManyPropSpecifier,
                    RepeatPropSpecifier,
                    PropSpecifier,
                ]
                subnodes = self.find(node, path)
                for subnode in subnodes:
                    propfuncname = self.find_property_func_name(subnode)
                    if propfuncname and propfuncname.lower() in funcnames_by_class[clsname.lower()]:
                        kept_methods.append(propfuncname.lower())

                ## Remove methods

                removed_methods = []
                path = [
                    Many,
                    ClassType,
                    Many,
                    ClassBody,
                    Many,
                    RepeatClassMember,
                    ClassMember,
                    ClassMemberInner,
                    MethodDecl,
                ]
                subnodes = self.find(node, path)
                for subnode in subnodes:
                    funcname = self.find_func_name(subnode)
                    if (funcname and
                        funcname.lower() not in kept_methods and
                        funcname.lower() in funcnames_by_class[clsname.lower()]):
                        removed_methods.append(funcname.lower())
                        subnode.parent.parent.unlink()

                kept.extend( map(lambda m: "%s.%s" % (clsname.lower(), m), kept_methods) )
                removed.extend( map(lambda m: "%s.%s" % (clsname.lower(), m), removed_methods) )

        return kept, removed

    def remove_funcsig_unitlevel(self, node, funcnames_whole):
        path = [
            Many,
            IntfdeclBlock,
            RepeatIntfdeclSection,
            IntfdeclSection,
            ProcedureIntfDecl,
        ]
        nodes = self.find(node, path)
        index = FuncIndex()
        for node in nodes:
            funcname = self.find_func_name(node)
            index.inc(funcname)
            if (funcname and index.get_labeled(funcname).lower() in funcnames_whole):
                node.parent.unlink()

    def remove_funcbody(self, node, funcnames_whole):
        path = [
            Many,
            ImpldeclBlock,
            RepeatImpldeclSection,
            ImpldeclSection,
            ProcedureImplDecl,
            ProcedureIntfDecl,
        ]
        nodes = self.find(node, path)
        index = FuncIndex()
        for node in nodes:
            funcname = self.find_func_name(node)
            index.inc(funcname)
            if (funcname and index.get_labeled(funcname).lower() in funcnames_whole):
                # check that func body is not a forward keyword
                path = [
                    ProcedureImplDecl,
                    ProcedureBodySemi,
                    ProcedureBody,
                    ForwardKw,
                ]
                if not self.find(node.parent, path):
                    node.parent.parent.unlink()

    def empty_funcbody(self, node, funcnames_whole):
        path = [
            Many,
            ImpldeclBlock,
            RepeatImpldeclSection,
            ImpldeclSection,
            ProcedureImplDecl,
            ProcedureIntfDecl,
        ]
        nodes = self.find(node, path)
        index = FuncIndex()
        for node in nodes:
            funcname = self.find_funcname_in_func(node)
            index.inc(funcname)
            if (funcname and index.get_labeled(funcname).lower() in funcnames_whole):
                # check that func body is not a forward keyword
                path = [
                    ProcedureImplDecl,
                    ProcedureBodySemi,
                    ProcedureBody,
                    ForwardKw,
                ]
                if not self.find(node.parent, path):
                    c, sig, nested, body = node.parent.children
                    nested = NestedDeclBlock()
                    seq = self.mk_funcbody_empty_sequence_stm()
                    body = ProcedureBodySemi(ProcedureBody(seq))
                    node.parent.set_children(c, sig, nested, body)

    def remove_funcs(self, node, funclist):
        funclist = map(string.lower, funclist)

        funcnames_in_class = {}
        funcnames_toplevel = {}
        for funcname in funclist:

            # check if funcname is clsname.funcname
            m = re.search('(?i)^([a-z0-9-]+)\.', funcname)
            if m:
                funcnames_in_class[funcname] = None
            else:
                funcnames_toplevel[funcname] = None

        # Empty all

        self.empty_funcbody(node, funcnames_in_class)
        self.empty_funcbody(node, funcnames_toplevel)
        return

        # Handle methods

#        kept, removed = self.remove_funcsig_classlevel(node, funcnames_by_class)
#        self.remove_funcbody(node, removed)
        self.empty_funcbody(node, funcnames_in_class)

        # Handle top level functions

        self.remove_funcsig_unitlevel(node, funcnames_toplevel)
        self.remove_funcbody(node, funcnames_toplevel)


class FuncIndex(object):
    def __init__(self):
        self.index = {}

    def inc(self, funcname):
        if funcname.lower() not in self.index:
            self.index[funcname.lower()] = 1
        else:
            self.index[funcname.lower()] += 1

    def get_labeled(self, funcname):
        return "%s{%s}" % (funcname, self.index[funcname.lower()])
