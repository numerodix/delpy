#!/usr/bin/env python
#
# Copyright: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

if __name__ == '__main__': import __path__

import re

from delpy import compilertools
from delpy.delphisrc import ast

class Unparser(object):
    nl = "\n"
    tablen = 2
    linewidth = 78

    @classmethod
    def override(cls, node):
        name = node.__name__
        func_stdname = "unparse_%s" % name
        func_ovname = "override_%s" % name
#        func_std = getattr(cls, func_stdname)
        func_ov = getattr(cls, func_ovname)
        setattr(cls, func_stdname, func_ov)

    def __init__(self):
        ast.nodes.bind_names_in_scope(globals())

        self.handlers = {}

        for key in dir(self):
            if key.startswith('unparse_'):
                m = re.search('^unparse_(.*)$', key)
                type_name = m.group(1)
                type_obj = eval(type_name)
                self.handlers[type_obj] = getattr(self, key)


    def get_tabs(self, indent):
        return (indent*self.tablen)*" "

    def strip_lst(self, lst):
        return filter(lambda item: item != "", lst)

    def safejoin(self, items, sep=""):
        if isinstance(items, basestring):
            return items

        items = self.strip_lst(items)
        for (i,item) in enumerate(items):
            if not isinstance(item, basestring):
                items[i] = self.unparse(item)

        return sep.join(items)

    def format_list(self, lst, indent=1):
        lst = self.strip_lst(lst)
        sep = ","
        tabs = self.get_tabs(indent)

        lines = []
        line = ""
        for (i, item) in enumerate(lst):
            line += self.unparse(item)
            if i < len(lst) - 1:
                line += sep
                if len(tabs) + len(line) >= self.linewidth:
                    lines.append(line)
                    line = ""
                else:
                    line += " "
        lines.append(line)

        s = tabs + (self.nl+tabs).join(lines)
        return s

    def format_block(self, *lst):
        if not lst:
            return ""

        newlst = []
        for item in lst:
            item = self.unparse(item)
            newlst.extend(item.split(self.nl))

        lst = self.strip_lst(newlst)
        sep = self.nl
        tabs = self.get_tabs(1)

        val = tabs + (sep+tabs).join(lst) + sep

        if len(val.strip()) == 0:
            return ""
        return val

    def lstrip(self, node):
        node = self.unparse(node)
        return node.lstrip()

    def rstrip(self, node):
        node = self.unparse(node)
        return node.rstrip()

    def padif(self, node, pre='', post=''):
        node = self.unparse(node)
        if len(node.strip()) == 0:
            return node
        return "%s%s%s" % (pre, node, post)

    def ifempty(self, node):
        node = self.unparse(node)
        if len(node.strip()) == 0:
            return node.strip()
        return node


    def unparse(self, node):
        result = None
        children = getattr(node, 'children', [])
        try:
            handler = self.handlers[type(node)]
            result = handler(node, children)
        except KeyError:
            result = []
            for child in children:
                result.append( self.unparse(child) )
        return self.safejoin(result)

    def unparse_str(self, node, *a, **kw):
        return node

    def unparse_unicode(self, node, *a, **kw):
        codec = compilertools.DelphiCompiler.get_dcc_charset()
        return node.encode(codec)


    ## Top level

    def unparse_Program(self, node, children):
        return children + [self.nl]

    def unparse_ProgramFile(self, node, children):
        progdecl, uses, impl, proc, dot = children
        uses = self.padif(uses, post=self.nl)
        impl = self.padif(impl, post=self.nl+self.nl)
        return [progdecl, uses, impl, proc, dot]

    def unparse_PackageFile(self, node, children):
        packdecl, reqs, contains, endkw, dot = children
        return [packdecl, reqs, contains, endkw, dot]

    def unparse_UnitFile(self, node, children):
        unitdecl, intf, impl, init, fin, endkw, dot = children
        return [unitdecl, intf, self.nl, impl, self.nl, init, fin, endkw, dot]

    def unparse_ProgramDeclProg(self, node, children):
        c, kw, name, opt, semi = children
        return [c, kw, ' ', name, opt, semi] + [self.nl]*2
    def unparse_ProgramDeclLib(self, node, children):
        c, kw, name, semi = children
        return [c, kw, ' ', name, semi] + [self.nl]*2
    def unparse_UnitDecl(self, *a):
        return self.unparse_ProgramDeclProg(*a)

    def unparse_InFilename(self, node, children):
        inkw, filename, c = children
        c = self.padif(c, pre=" ")
        c = self.rstrip(c)
        return [inkw, ' ', filename, c]

    def unparse_ImplementationSection(self, node, children):
        implkw, uses, body = children
        uses = self.padif(uses, pre=self.nl)
        body = self.padif(body, pre=self.nl, post=self.nl)
        return [implkw, uses, body]

    def unparse_InterfaceSection(self, node, children):
        intfkw, uses, body = children
        uses = self.padif(uses, pre=self.nl)
        body = self.padif(body, pre=self.nl)
        return [intfkw, uses, body]

    def unparse_InitializationSection(self, node, children):
        kw, body = children
        return [kw, self.nl, body, self.nl]
    def unparse_FinalizationSection(self, *a):
        return self.unparse_InitializationSection(*a)

    def unparse_RepeatIntfdeclSection(self, node, children):
        return self.safejoin(children, sep=self.nl)

    def unparse_RepeatImpldeclSection(self, node, children):
        return self.safejoin(children, sep=self.nl+self.nl)

    def unparse_InterfaceKw(self, node, children):
        return children + [self.nl]
    def unparse_ImplementationKw(self, *a):
        return self.unparse_InterfaceKw(*a)

    ## Comments

    def unparse_ManyComments(self, node, children):
        return children + [self.nl]

    def unparse_RepeatAnycomment(self, node, children):
        return self.safejoin(children, sep=self.nl)

    ## Imports

    def unparse_UsesClause(self, node, children):
        c, kw, lst, semi = children
        return [c, kw, self.nl, lst, semi, self.nl]

    def unparse_ListUsesItem(self, node, children):
        return self.format_list(children) 

    def unparse_UsesItem(self, node, children):
        c, qualid, infile = children
        infile = self.padif(infile, pre=" ")
        return [c, qualid, infile]

    ## Var/type/const declarations

    def unparse_VarSection(self, node, children):
        c, kw, body = children
        return [c, kw, self.nl, body]
    def unparse_TypeSection(self, *a):
        return self.unparse_VarSection(*a)
    def unparse_ConstSection(self, *a):
        return self.unparse_VarSection(*a)
    def unparse_ResourceSection(self, *a):
        return self.unparse_VarSection(*a)

    def unparse_ExportsSection(self, node, children):
        c, exkw, lst, semi = children
        return [c, exkw, self.nl, lst, semi]

    def unparse_VariantSection(self, node, children):
        casekw, idcol, typ, ofkw, body = children
        idcol = self.padif(idcol, pre=" ")
        body = self.format_block(body)
        return [casekw, idcol, ' ', typ, ' ', ofkw, self.nl, body]

    def unparse_ListExportsEntry(self, node, children):
        return self.format_list(children) 

    def unparse_RepeatVarDecl(self, node, children):
        return self.format_block(*children)
    def unparse_RepeatTypeDecl(self, *a):
        return self.unparse_RepeatVarDecl(*a)
    def unparse_RepeatConstantDecl(self, *a):
        return self.unparse_RepeatVarDecl(*a)

    def unparse_VarDecl(self, node, children):
        c, idlist, coltyp, hintdir, varinit, semi = children
        varinit = self.padif(varinit, pre=" ")
        return [c, idlist, coltyp, hintdir, varinit, semi]

    def unparse_ConstantDecl(self, node, children):
        c, idlist, spec, hintdir, semi = children
        hintdir = self.padif(hintdir, pre=" ")
        return [c, idlist, spec, hintdir, semi]

    def unparse_AbsoluteInit(self, node, children):
        return self.safejoin(children, sep=" ")

    def unparse_RepeatNestedDeclSection(self, node, children):
        elems = self.safejoin(children, self.nl)
        return elems

    def unparse_ConstantSpecEqual(self, node, children):
        eq, expr = children
        return [' ', eq, ' ', expr]
    def unparse_ConstInit(self, *a):
        return self.unparse_ConstantSpecEqual(*a)

    ## Interfaces

    def unparse_InterfaceType(self, node, children):
        intkw, heritagelist, guid, body = children
        body = self.padif(body, pre=self.nl)
        return [intkw, heritagelist, guid, body]

    ## Records

    def unparse_RepeatRecordVariant(self, node, children):
        return self.safejoin(children, sep=self.nl)

    def unparse_RecordVariantComp(self, node, children):
        exprs, col1, lparen, idlist, col2, typ, rparen, semi = children
        return [exprs, col1, ' ', lparen, idlist, col2, ' ', typ, rparen, semi]

    def unparse_RecordVariantInt(self, node, children):
        exprs, col, lparen, body, rparen, semi = children
        return [exprs, col, ' ', lparen, body, rparen, semi]

    ## Classes

    def unparse_ClassType(self, node, children):
        packedkw, classkw, abstractkw, heritage, body = children
        packedkw = self.padif(packedkw, post=" ")
        abstractkw = self.padif(abstractkw, pre=" ")
        body = self.padif(body, pre=self.nl)
        return [packedkw, classkw, abstractkw, heritage, body]

    def unparse_HeritageListHelper(self, node, children):
        helper_forkw, id = children
        return [' ', helper_forkw, ' ', id]

    def unparse_VisibilityDefault(self, node, children):
        return self.format_block(*children)
    def unparse_RepeatVisibilityBlock(self, *a):
        return self.unparse_VisibilityDefault(*a)

    def unparse_VisibilityKwStrictPrivate(self, node, children):
        return self.safejoin(children, sep=" ")

    def unparse_VisibilityBlock(self, node, children):
        kw, body = children
        return [kw, self.nl, body]

    def unparse_RepeatClassMember(self, node, children):
        return self.format_block(*children)

    def unparse_ClassMemberComp(self, node, children):
        return self.safejoin(children, sep=" ")

    def unparse_PropertyDecl(self, node, children):
        kw, name, indexes, type, spec, defarr, semi = children
        return [kw, ' ', name, indexes, type, spec, defarr, semi]

    def unparse_PropSpecifier(self, node, children):
        return [' '] + children

    def unparse_StoredSpec(self, node, children):
        return self.safejoin(children, sep=" ")

    def unparse_DefaultSpec(self, node, children):
        return self.safejoin(children, sep=" ")

    def unparse_DispidSpec(self, node, children):
        return self.safejoin(children, sep=" ")

    def unparse_IndexSpec(self, node, children):
        indexkw, ex = children
        return [indexkw, ' ', ex]

    def unparse_AccessorVerbId(self, node, children):
        c, verb, id = children
        return [c, verb, ' ', id]

    ## Functions

    def unparse_ProcedureImplDecl(self, node, children):
        c, sig, nested, body = children
        body = self.unparse(body)
        if body.startswith('forward'):
            sig = self.rstrip(sig)
            sig = sig + ' '
        return [c, sig, nested, body]

    def unparse_NestedProcedureImplDecl(self, node, children):
        return self.format_block(*children)

    def unparse_ProceduralType(self, node, children):
        prochead, ofobj, callspec = children
        prochead = self.rstrip(prochead)
        ofobj = self.padif(ofobj, pre=" ")
        callspec = self.padif(callspec, pre=" ")
        return [prochead, ofobj, callspec]

    def unparse_ProcedureIntfDecl(self, node, children):
        return children + [self.nl]

    def unparse_ProcedureSignature(self, node, children):
        classkw, prockw, name, params, typ = children
        classkw = self.padif(classkw, post=" ")
        return [classkw, prockw, ' ', name, params, typ]

    def unparse_SemiFormalParameter(self, node, children):
        semi, formal = children
        return [semi, ' ', formal]

    def unparse_ParmQual(self, node, children):
        return children + [' ']

    def unparse_SemiDirective(self, node, children):
        semi, direc = children
        return [semi, ' ', direc]

    def unparse_ProcedureExternalDecl(self, node, children):
        sig, extern, callspec, semi = children
        sig = self.rstrip(sig)
        extern = self.padif(extern, pre=" ")
        callspec = self.padif(callspec, pre=" ")
        return [sig, extern, callspec, semi]

    def unparse_ExternalDirective(self, node, children):
        externalkw, expr, name = children
        expr = self.padif(expr, pre=" ")
        name = self.padif(name, pre=" ")
        return [externalkw, expr, name]

    def unparse_ExternalName(self, node, children):
        return self.safejoin(children, sep=" ")

    def unparse_DirectiveDispid(self, node, children):
        dispidkw, sign, number = children
        return [dispidkw, ' ', sign, number]

    def unparse_DirectiveMessagePlusNumber(self, node, children):
        return self.safejoin(children, sep=" ")

    def unparse_DirectiveMessage(self, node, children):
        return self.safejoin(children, sep=" ")

    ## Statements

    def unparse_SequenceStm(self, node, children):
        c, beg, body, end = children
        return [c, beg, self.nl, body, end]

    def unparse_StatementList(self, node, children):
        stm_semis, stm = children
        if stm:
            stm = self.format_block(stm)
        return [stm_semis, stm]

    def unparse_RepeatStatementSemi(self, node, children):
        return self.format_block(*children)

    def unparse_StatementSemiComp(self, node, children):
        stm, c, semi = children
        stm = self.rstrip(stm)
        c = self.ifempty(c)
        return [stm, c, semi]

    def unparse_LabelDecl(self, node, children):
        labelkw, id, semi = children
        return [labelkw, ' ', id, semi, self.nl]

    def unparse_ListLabelId(self, node, children):
        return self.safejoin(children, sep=", ")

    def unparse_AssignStm(self, node, children):
        sym, eq, ex = children
        return [sym, ' ', eq, ' ', ex]

    def unparse_CommaArgm(self, node, children):
        comma, arg = children
        return [comma, ' ', arg]

    def unparse_IfStm(self, node, children):
        ifkw, test, thenkw, body, elseexp = children
        body = self.format_block(body)
        return [ifkw, ' ', test, ' ', thenkw, self.nl, body, elseexp]

    def unparse_ElseStm(self, node, children):
        c, elsekw, body = children
        body = self.unparse(body)
        if body.startswith("if"):
            body = ' ' + body
        else:
            body = self.format_block(body)
            body = self.padif(body, pre=self.nl)
        return [self.nl, c, elsekw, body]

    def unparse_TryExceptStm(self, node, children):
        return self.safejoin(children, sep=self.nl)
    def unparse_TryFinallyStm(self, *a):
        return self.unparse_TryExceptStm(*a)

    def unparse_ExceptionBlockComp(self, node, children):
        handlerlist, elseblock = children
        return [handlerlist, self.nl, elseblock]

    def unparse_ExceptionHandler(self, node, children):
        onkw, evar, typ, dokw, body = children
        evar = self.padif(evar, post=" ")
        body = self.format_block(body)
        body = self.rstrip(body)
        return [onkw, ' ', evar, typ, ' ', dokw, self.nl, body]

    def unparse_WithStm(self, node, children):
        kw, test, dokw, body = children
        body = self.format_block(body)
        return [kw, ' ', test, ' ', dokw, self.nl, body]
    def unparse_WhileStm(self, *a):
        return self.unparse_WithStm(*a)

    def unparse_ForStmCount(self, node, children):
        forkw, var, eq, begexpr, down_to, endexpr, dokw, body = children
        body = self.format_block(body)
        return [forkw, ' ', var, ' ', eq, ' ', begexpr, ' ', down_to, ' ',
                endexpr, ' ', dokw, self.nl, body]

    def unparse_ForInStm(self, node, children):
        forkw, id, inkw, qualid, dokw, body = children
        body = self.format_block(body)
        return [forkw, ' ', id, ' ', inkw, ' ', qualid, ' ', dokw, self.nl,
                body]

    def unparse_RepStm(self, node, children):
        repkw, body, untilkw, cond = children
        return [repkw, self.nl, body, self.nl, untilkw, ' ', cond]

    def unparse_CaseStm(self, node, children):
        casekw, test, ofkw, selector, caseelse, end = children
        return [casekw, ' ', test, ' ', ofkw, self.nl, selector, caseelse,
                self.nl, end]

    def unparse_CaseElse(self, node, children):
        c, elsekw, body = children
        return [c, elsekw, self.nl, body]

    def unparse_RepeatCaseSelector(self, node, children):
        return self.format_block(*children)

    def unparse_CaseSelector(self, node, children):
        labels, colon, body, semi = children
        body = self.format_block(body)
        body = self.rstrip(body)
        return [labels, colon, self.nl, body, semi]

    def unparse_RaiseStm(self, node, children):
        raisekw, ex, at = children
        ex = self.padif(ex, pre=" ")
        at = self.padif(at, pre=" ")
        return [raisekw, ex, at]

    def unparse_GotoStm(self, node, children):
        gotokw, label = children
        return [gotokw, ' ', label]

    def unparse_AtAddress(self, node, children):
        atkw, ad = children
        return [atkw, ' ', ad]

    ## Expressions

    def unparse_ListExpr(self, node, children):
        return self.safejoin(children, sep=", ")

    def unparse_ListQualifiedId(self, node, children):
        return self.safejoin(children, sep=", ")

    def unparse_ListId(self, node, children):
        return self.safejoin(children, sep=", ")

    def unparse_ListPropIndexName(self, node, children):
        return self.safejoin(children, sep=",")

    def unparse_PropIndexName(self, node, children):
        modkw, id = children
        modkw = self.padif(modkw, post=" ")
        return [modkw, id]

    # XXX split lines when list is too long
    def unparse_RepeatInfixExpr(self, node, children):
        joined = self.safejoin(children)
        if len(joined) > self.linewidth:
            joined = self.safejoin(children, sep=self.nl)
            joined = self.format_block(joined)
            joined = self.padif(joined, pre=self.nl)
        return joined

    def unparse_InfixExpr(self, node, children):
        op, ex = children
        op = self.unparse(op)
        if op == "^":
            return [op, ex]
        return [' ', op, ' ', ex]

    def unparse_SetConstructor(self, node, children):
        lbracket, setelem, commaelems, rbracket = children
        commaelems = self.format_block(commaelems)
        commaelems = self.padif(commaelems, post=self.nl)
        commaelems = self.lstrip(commaelems)
        commaelems = self.ifempty(commaelems)
        if commaelems:
            setelem = self.format_block(setelem)
            setelem = self.padif(setelem, pre=self.nl)
            setelem = self.rstrip(setelem)
            setelem = self.ifempty(setelem)
        return [lbracket, setelem, commaelems, rbracket]

    def unparse_CommaSetElement(self, node, children):
        comma, elem = children
        return [comma, self.nl, elem]

    def unparse_ListCaseLabel(self, node, children):
        return self.safejoin(children, sep=","+self.nl)

    def unparse_ListEnumSpec(self, node, children):
        joined = self.safejoin(children, sep=","+self.nl)
        joined = self.format_block(joined)
        return [self.nl, joined]

    def unparse_ListArrayIndex(self, node, children):
        return self.safejoin(children, sep=", ")

    def unparse_RecordConstant(self, node, children):
        lparen, many, one, rparen = children
        one = self.padif(one, pre=" ")
        return [lparen, many, one, rparen]

    def unparse_RepeatRecordFieldConstantSemi(self, node, children):
        return self.safejoin(children, sep=" ")

    def unparse_PrefixOprSpaced(self, node, children):
        return children + [' ']

    def unparse_DotdotExpr(self, node, children):
        dots, expr = children
        dots = self.unparse(dots)
        dots = dots.replace(' ', '')
        return [dots, expr]

    def unparse_CommaId(self, node, children):
        comma, id = children
        return [comma, ' ', id]

    ## Types

    def unparse_TypeDecl(self, node, children):
        c, idlist, eq, typekw, spec, hintdir, semi = children
        typekw = self.padif(typekw, post=" ")
        hintdir = self.padif(hintdir, pre=" ")
        return [c, idlist, ' ', eq, ' ', typekw, spec, hintdir, semi]

    def unparse_ClassReferenceType(self, node, children):
        class_ofkw, body = children
        return [class_ofkw, ' ', body]

    def unparse_ListTypedConst(self, node, children):
        joined = self.safejoin(children, sep=","+self.nl)
        joined = self.format_block(joined)
        return [self.nl, joined]

    def unparse_ColonType(self, node, children):
        col, typ = children
        return [col, ' ', typ]

    def unparse_ArrayOfConst(self, node, children):
        arraykw, body = children
        return [arraykw, ' ', body]

    def unparse_ArrayPacked(self, node, children):
        packedkw, arraykw, indexlist, ofbasetype = children
        packedkw = self.padif(packedkw, post=" ")
        return [packedkw, arraykw, indexlist, ofbasetype]

    def unparse_OfBasetype(self, node, children):
        ofkw, baset = children
        return [' ', ofkw, ' ', baset]

    ## Assembly

    def unparse_AsmStmtblock(self, node, children):
        asmkw, body, endkw = children
        body = self.format_block(body)
        return [asmkw, self.nl, body, endkw]

    def unparse_RepeatAsmStm(self, node, children):
        return self.safejoin(children, sep=self.nl)

    def unparse_AsmlabelColon(self, node, children):
        asmlab, colon = children
        return [' ', self.nl, asmlab, colon, self.nl]

    def unparse_AsmUnlabeledstm(self, node, children):
        joined = self.safejoin(children, sep=" ")
        joined = self.format_block(joined)
        return joined

    def unparse_ListAsmExpr(self, node, children):
        return self.safejoin(children, sep=", ")

    def unparse_AsmExpr(self, node, children):
        term, infixexpr = children
        infixexpr = self.padif(infixexpr, pre=" ")
        return [term, infixexpr]

    def unparse_AsmInfixExpr(self, node, children):
        infixop, term = children
        return [infixop, ' ', term]

    def unparse_AsmTermComp(self, node, children):
        prefixop, primary, postfixop = children
        prefixop = self.padif(prefixop, post=" ")
        postfixop = self.padif(postfixop, pre=" ")
        return [prefixop, primary, postfixop]



    def override_StatementList(self, node, children):
        return self.format_block(*children)

    def override_Identlist(self, node, children):
        return self.safejoin(children, sep=", ")

    def override_SetConstructor(self, node, children):
#        args = self.safejoin(children, sep=", "+self.nl)
#        args = self.format_block(args)
#        return ['[', self.nl, args, ']']
        args = self.safejoin(children, sep=", ")
        return ['[', args, ']']

    def override_FormalParameters(self, node, children):
        args = self.safejoin(children, sep="; ")
        if len(args) > 40:
            args = self.safejoin(children, sep="; "+self.nl)
            args = self.format_block(args)
            return ['(', self.nl, args, ')']
        return ['(', args, ')']

    def override_Arguments(self, node, children):
        args = self.safejoin(children, sep=", ")
        if len(args) > 40:
            args = self.safejoin(children, sep=", "+self.nl)
            args = self.format_block(args)
            return ['(', self.nl, args, ')']
        return ['(', args, ')']


def unparse(node):
    return Unparser().unparse(node)
