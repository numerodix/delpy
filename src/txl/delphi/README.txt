TXL Grammar for Borland Delphi 2006 

Jorge L. Cangas, December 2007

delphi.grammar : 
    Main grammar file. Contains support for Delphi 2006 features.
    - class helpers.
    - for in enunerator oriented loops.

    Then the grammar allow things that not will compile. Of course we have yet a Delphi compiler:
    The grammar is oriented to allow TXL transformations, so some things are 'unified' in any way.
    The idea is: "if it compile, it pass the txl grammar: then can be transformed easy"

delphi_comment_overr.grammar: 
    Grammar overrides for comments. The block comments are managed in 
    the grammar (not in comments section), in order to diferentiate 'pure' comments from preprocessor
    instructions.

delphidfm.grammar: 
    Grammar to parse .dfm Delphi Form files. Of course the .dfm need saved 
    in text format (Editor context menu) o with the convert tool (in $(Delphi)/bin)

delphipp.grammar: 
    Grammar to parse preprocessor code

asm.grammmar: 
    You can include this in your TXL prpogramm if you use assembler in your delphi code.
    I don't understand asm very good: I extracted this grammar from Delphi documentation.

I tested these grammars with Delphi VCL & RTL source code.
If you enhance something, please let me know at jorge.cangas@gmail.com

-------------------------------------------------------------------------------

Revised by Martin Matusiak in 2010:

- opt/repeat nodes have been found problematic, because they will appear or
not appear in the parse depending on the input. To get around this they have
been wrapped with an additional static node that is always present:

From:

define directive_message
	'message [opt qualified_id]
end define

To:

define directive_message
	'message [box_qualified_id]
end define

define box_qualified_id
	[opt qualified_id]
end define

This is a hack, because it [needlessly] inflates the grammar.

- delphi_comment.grammar contains only the necessary definition for
comments, but no overrides. The idea of parsing Delphi without comments is in
my view impractical.

The grammar has been used in the delpy project, see: 
http://sourceforge.net/projects/delpysuite/
