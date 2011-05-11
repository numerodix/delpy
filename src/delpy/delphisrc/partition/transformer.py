#!/usr/bin/env python
#
# Copyright: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

if __name__ == '__main__': import __path__

from delpy.delphisrc import ast
from delpy.delphisrc import constructor
from delpy.delphisrc import finder
from delpy.delphisrc import transformer
from delpy.delphisrc import unparser

class Transformer(transformer.Transformer):
    def __init__(self):
        transformer.Transformer.__init__(self)
        ast.nodes.bind_names_in_scope(globals())

    def format_stm_to_comment(self, node):
        if type(node) != StatementSemi:
            node = self.mk_statement_semi(node)
        stm_s = unparser.unparse(node)
        comm_s = "{ REMOTED:\n  %s\n}" % stm_s
        return self.mk_commentlist(comm_s)

    def mk_Call_recvInts(self, funcname, vs, args=None):
        int_lst = map(lambda var: self.mk_term_with_prefix('@', var), vs)
        bool_lst = map(lambda var:
                       self.mk_term(self.mk_qualified_id('SocketTypes.transFlat')), vs)

        callargs = [
            self.mk_qualified_id(funcname),
            self.mk_term(
                self.mk_set_constructor(*int_lst)
            ),
            self.mk_term(
                self.mk_set_constructor(*bool_lst)
            )
        ]
        if args:
            args = map(self.mk_term, args)
            callargs.insert(1, *args)

        t_call = self.mk_func_call(*callargs)
        t = self.mk_statement_semi(self.mk_call_stm(t_call))
        return t

    def mk_Call_sendInts(self, funcname, vs, args=None, comment=None):
        int_lst = map(lambda var: self.mk_term_with_prefix('@', var), vs)
        size_lst = map(lambda var:
                       self.mk_term(
                           self.mk_func_call(
                               self.mk_qualified_id('SizeOf'),
                               self.mk_term(var)
                           )
                       ),
                       vs)
        bool_lst = map(lambda var:
                       self.mk_term(self.mk_qualified_id('SocketTypes.transFlat')), vs)

        callargs = [self.mk_qualified_id(funcname)]
        if int_lst:
            callargs.extend([
                self.mk_term(
                    self.mk_set_constructor(*int_lst)
                ),
                self.mk_term(
                    self.mk_set_constructor(*size_lst)
                ),
                self.mk_term(
                    self.mk_set_constructor(*bool_lst)
                )
            ])
        if args:
            args = map(self.mk_term, args)
            callargs.insert(1, *args)

        t_call = self.mk_func_call(*callargs)
        t = self.mk_statement_semi(self.mk_call_stm(t_call), comment=comment)
        return t

    def mangle_funcname(self, funcname):
        return 'Serve__%s' % funcname.replace('.', '_')

    def mk_Func_InitIndex(self, *funcnames):
        func_initindex = 'InitIndex'
        func_registerhandler = 'HandlerIndex.Register'

        funcnames_mangled = map(self.mangle_funcname, funcnames)

        stms = []
        stms.append(
            self.mk_statement_semi(self.mk_assign_stm(
                    self.mk_qualified_id('HandlerIndex'),
                    self.mk_func_call(
                        self.mk_qualified_id('TServiceHandlerIndex.Create')
                    ))))
        for (name, mangled) in zip(funcnames, funcnames_mangled):
            call = self.mk_func_call(
                self.mk_qualified_id(func_registerhandler),
                self.mk_term(self.mk_char_lit(name)),
                self.mk_term(self.mk_qualified_id(mangled))
            )
            t = self.mk_statement_semi(
                self.mk_call_stm(call))
            stms.append(t)

        pred = self.mk_expression_predicate(
            self.mk_qualified_id('HandlerIndex'), '=', 'nil')
        ifstm = self.mk_statement_semi(self.mk_if_stm(pred, *stms))

        func_sig = self.mk_procedure_intf_decl(
            self.mk_procedure_id(func_initindex))
        t = self.mk_procedure_impl_decl(func_sig,
                                        self.mk_statement_block(ifstm))
        return t

    def mk_Func_Handler(self, callnode, funcname, args=None, assign_var=None):
        def mk_param(qual, name, typename):
            typespec = self.mk_type_spec(typename)
            param = self.mk_formal_parameter(name, typespec=typespec, qualifier=qual)
            return param

        mangled = self.mangle_funcname(funcname)
        proc_id = self.mk_procedure_id(mangled)
        params = [
            mk_param('const', 'instream', 'TMemoryStream'),
            mk_param('const', 'outstream', 'TMemoryStream'),
        ]
        func_sig = self.mk_procedure_intf_decl(proc_id, params)

        localvars = []
        if args:
            localvars.extend(args)
        if assign_var:
            localvars.append(assign_var)

        var_sec = None
        if localvars:
            typespec = self.mk_type_spec_simple('integer')
            var_decl = self.mk_var_decl(localvars, typespec)
            var_sec = self.mk_var_section(var_decl)

        stms = []
        if args:
            stms.append(
                self.mk_Call_recvInts('SocketMarshall.Read', args,
                                      args=['instream'])
            )
        stms.append(callnode)
        if assign_var:
            stms.append(
                self.mk_Call_sendInts('SocketMarshall.Write', [assign_var],
                                      args=['outstream'])
            )

        t = self.mk_procedure_impl_decl(
            func_sig,
            self.mk_statement_block(*stms),
            nesteds=[var_sec],
        )
        return t

    def remote(self, node):
        func_readints = 'SocketClient.Receive'
        func_writeints = 'SocketClient.Transmit'

        cs = '{ #remote }'

        remoted = []
        handlers = []

        comments = self.find_comment_matching(node, cs)
        for cnode in comments:

            # AssignStm
            path = [
                Many,
                AssignStm,
            ]
            trees = self.find(cnode, path, rec=True)
            for tree in trees:
                treesemi = tree.parent.parent.parent.parent.parent.parent

                variable, expr = self.find_assign_stm_operands(tree)
                variable_s = self.find_string(variable)
                funcname = self.find_by_type(expr, QualifiedId)[0]
                funcname_s = self.find_string(funcname)
                argms = self.find_func_call_args(tree)
                argnames = map(lambda n: self.find_by_type(n, QualifiedId)[0], argms)
                argnames_s = map(self.find_string, argnames)

                remoted.append(funcname_s)
                handlers.append(
                    self.mk_Func_Handler(self.mk_statement_semi(tree),
                                         funcname_s,
                                         args=argnames_s,
                                         assign_var=variable_s)
                )

                stms = []

                treesemi_c = self.format_stm_to_comment(tree)
                stmsnd = self.mk_Call_sendInts(func_writeints, argnames,
                                               args=[self.mk_char_lit(funcname_s)],
                                               comment=treesemi_c)
                stms.append(stmsnd)

                stmthd = self.mk_Call_recvInts(func_readints, [variable])
                stms.append(stmthd)

                treesemi.replace_with(*stms)

        initfunc = self.mk_Func_InitIndex(*remoted)
        handlers.insert(0, initfunc)
        return handlers
