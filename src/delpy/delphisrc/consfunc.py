#!/usr/bin/env python
#
# Copyright: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

if __name__ == '__main__': import __path__

import re

from delpy.delphisrc import ast

class Constructor(object):
    def __init__(self):
        ast.nodes.bind_names_in_scope(globals())

    def mk_procedure_id(self, *args):
        args = list(args)
        arg_last = args.pop()
        last = Id(arg_last)

        items = map(self.mk_namespace, args)
        items = map(lambda x: OptNamespace(x), items)
        items.append(last)

        return ProcedureId(*items)

    def mk_formal_parameter(self, name, typespec=None, qualifier=None):
        param_qual = BoxParmQual()
        if qualifier:
            param_qual = BoxParmQual(OptParmQual(ParmQual(qualifier)))

        list_id = ListId(Id(name))
        items = [list_id]

        if typespec:
            param_type = ParameterType(self.mk_colon_type(typespec))
            param_type = OptParameterType(param_type)
            items.append(param_type)

        parameter = Parameter(*items)

        t = FormalParameter(Commentlist(), param_qual, parameter)
        return t

    def mk_procedure_intf_decl(self, proc_id, params=None, type=None):
        proc_kw = 'procedure'
        if type:
            proc_kw = 'function'

        proc_kw = ProcedureKeyword(proc_kw)
        proc_id = BoxProcedureId(OptProcedureId(proc_id))
        boxparams = BoxFormalParameters()
        if params:
            boxparams = OptFormalParameters(FormalParameters(*params))
            boxparams = BoxFormalParameters(boxparams)
        ret_type = BoxColonType()
        if type:
            ret_type = BoxColonType(OptColonType(self.mk_colon_type(type)))

        proc_sig = ProcedureSignature(BoxClass(), proc_kw, proc_id, boxparams, ret_type)
        t = ProcedureIntfDecl(
            Commentlist(),
            proc_sig,
            BoxSemi(OptLiteral(Literal(";")))
        )
        return t

    def mk_func(self):
        def mk_procsig():
            proc_id = self.mk_procedure_id('Serve__Core_ComputePrice')
            param_type = TypeSpec(
                Commentlist(),
                TypeSpecInner(self.mk_qualified_id('TIdTCPConnection'))
            )
            link_param = self.mk_formal_parameter('Link', param_type, 'const')
#            self.p(proc_id)
#            self.p(link_param)
            proc_sig = self.mk_procedure_intf_decl(proc_id, [link_param])
            return proc_sig

        def mk_varsec():
            int_type = TypeSpec(
                Commentlist(),
                TypeSpecInner(SimpleType(OrdinalType(IntegerType('integer'))))
            )
            var_decl = self.mk_var_decl(['i1', 'i2'], int_type)
            var_sec = self.mk_var_section(var_decl)
            return var_sec

        def mk_stms():
            fname_qid1 = self.mk_qualified_id('Link', 'ReadInteger')
            fname_qid2 = self.mk_qualified_id('Link', 'ReadInteger')
            fname_qid3 = self.mk_qualified_id('Core', 'ComputePrice')
            fname_qid4 = self.mk_qualified_id('Link', 'WriteInteger')
            fcall1 = self.mk_func_call(fname_qid1)
            fcall2 = self.mk_func_call(fname_qid2)
            fcall3 = self.mk_func_call(fname_qid3, 'i1', 'i2')
            fcall4 = self.mk_func_call(fname_qid4, fcall3)
            ass1 = self.mk_assign_stm(self.mk_qualified_id('i1'), fcall1)
            ass2 = self.mk_assign_stm(self.mk_qualified_id('i2'), fcall2)
            calls = self.mk_call_stm(fcall4)
            stm_semi1 = self.mk_statement_semi(ass1)
            stm_semi2 = self.mk_statement_semi(ass2)
            stm_semi3 = self.mk_statement_semi(calls)
            return self.mk_statement_block(stm_semi1, stm_semi2, stm_semi3)

        proc_sig = mk_procsig()
#        self.p(proc_sig)

        var_sec = mk_varsec()
#        self.p(var_sec)

        stms = mk_stms()
#        self.p(stms)

        nest = NestedDeclBlock(RepeatNestedDeclSection(NestedDeclSection(var_sec)))
        body = ProcedureBodySemi(ProcedureBody(stms), ';')

        t = ProcedureImplDecl(
            Commentlist(),
            proc_sig,
            nest,
            body
        )
#        self.p(t)
        return t

    def mk_procedure_impl_decl(self, proc_sig, stmlist, nesteds=None):
        nest = NestedDeclBlock()
        if nesteds:
            nesteds = map(NestedDeclSection, nesteds)
            nest = NestedDeclBlock(RepeatNestedDeclSection(*nesteds))
        body = ProcedureBodySemi(ProcedureBody(stmlist), ';')

        t = ProcedureImplDecl(
            Commentlist(),
            proc_sig,
            nest,
            body
        )
        return t
