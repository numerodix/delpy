# The parser

Internally, `delpy` uses the parser from the [TXL transformation
system](http://txl.ca/). This made it possible to use an existing parser and
grammar.


## Parsing with TXL

The tool `txlparser.py` executes the TXL parser and returns the parse tree in
xml.

Parse trees grow quickly with the size of the program, so let's use a minimal program:

	program Trivial;

	begin
	end.

The resulting parse tree:

	$ txlparser.py readxml/Trivial.dpr
	<program>
	 <delphi_file><program_file>
	   <program_decl>
		<program_decl_prog>
		 <commentlist></commentlist> program
		 <qualified_id>
		  <name><id>Trivial</id></name>
		 </qualified_id>
		 <box_program_file_list></box_program_file_list> ;
		</program_decl_prog>
	   </program_decl>
	   <box_uses_clause></box_uses_clause>
	   <impldecl_block></impldecl_block>
	   <procedure_body><sequence_stm>
		 <commentlist></commentlist>
		 <begin_kw>begin</begin_kw>
		 <statement_list>
		  <many_statement_semi></many_statement_semi>
		  <box_statement></box_statement>
		 </statement_list>
		 <end_kw>
		  <commentlist></commentlist> end
		 </end_kw>
		</sequence_stm>
	   </procedure_body>
	   <file_end>.</file_end>
	  </program_file>
	 </delphi_file>
	</program>

If the parsing fails the parser will output an error and you can inspect this
using the `-v` option:

	$ txlparser.py -v trivial/NamespaceExample.pas
	...
	Parsing NamespaceExample.pas ...
	[NamespaceExample.pas, ../../txl/delphi/pas.txl] : TXL0192E line 19 of NamespaceExample.pas - Syntax error at or near:
			. Windows . Forms . >>> Label <<< ; LabelProductVersion : System .


## Delphi parse trees in Python

The tool `delphiparser.py` uses `txlparser.py` to obtain a parse tree in xml,
parses the xml and produces a representation of the parse tree using Python
objects. Use the `-t` option to inspect the parse tree:

	$ delphiparser.py readxml/Trivial.dpr -t
	Program(
	  DelphiFile(
		ProgramFile(
		  ProgramDecl(
			ProgramDeclProg(
			  Commentlist()
			, "program"
			, QualifiedId(Name(Id("Trivial")))
			, BoxProgramFileList()
			, ";"
			)
		  )
		, BoxUsesClause()
		, ImpldeclBlock()
		, ProcedureBody(
			SequenceStm(
			  Commentlist()
			, BeginKw("begin")
			, StatementList()
			, EndKw(Commentlist(), "end")
			)
		  )
		, FileEnd(".")
		)
	  )
	)
