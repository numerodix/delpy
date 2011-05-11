# Preprocessing a codebase

We have seen [before](viewgraph.html#Preprocessor_statements) how preprocessor
statements in source code can be a source of problems for program tracing. 
The problem
is even more serious for wholesale parsing of source code, because the
preprocessor and Delphi are effectively two languages mixed together. When a
program is compiled, the preprocessor code is evaluated first, producing a file
that only has Delphi left. *This* is the Delphi source code that effectively is
compiled.

Evaluating the preprocessor code is thus a sort of partial compilation of the
program, from preprocessor/Delphi down to Delphi.

Unfortunately, BDS has no tool for preprocessing, but there is a preprocessor
called [DIPP](http://www.yunqa.de/delphi/doku.php/products/dipp/index) 
written by Ralf Junker. The `preprocess.py` tool uses `DIPP` internally.

You can preprocess a single file or a codebase at large, but you have to know
two things:

1. Which compiler directives to set. These are flags like `H-`, `R+` and are 
listed in the `DelphiCompilerFlags` file.
1. Which compiler conditionals to set. These are symbols like `DEBUG` can
either be set or not set. These are also listed in the `DelphiCompilerFlags`
file.

You can preprocess without setting either one, but then your program may not
evaluate correctly.

You then run the tool:

	$ preprocess.py -d "H-;R+" -c "DEBUG;WIN" Root.dpr
	>> Preprocessing includes in Root.dpr ...
	 [/home/frank/code/samples/preproc] + wine /home/frank/code/dipp/dipp-1.6.1.exe \
		 Root.dpr /tmp/.Root.dpr -o -PD2006 -li
	The Delphi Inspiration Pascal Preprocessor - Version 1.6.1
	Copyright (c) 2003-2010 Ralf Junker, The Delphi Inpiration
	http://www.yunqa.de/delphi/
	In:  Z:\home\frank\code\samples\preproc\Root.dpr
	Out: Z:\tmp\.Root.dpr
	  Processed 16 lines in 1 ms.
	* DONE ...
	>> Preprocessing conditionals in Root.dpr ...
	 [/home/frank/code/samples/preproc] + wine /home/frank/code/dipp/dipp-1.6.1.exe \
		 Root.dpr /tmp/.Root.dpr -o -PD2006 -c -h '-DDEBUG;WIN'
	The Delphi Inspiration Pascal Preprocessor - Version 1.6.1
	Copyright (c) 2003-2010 Ralf Junker, The Delphi Inpiration
	http://www.yunqa.de/delphi/
	In:  Z:\home\frank\code\samples\preproc\Root.dpr
	Out: Z:\tmp\.Root.dpr
	  Processed 16 lines in 0 ms.
	* DONE ...

Preprocessing happens in two steps:

1. File includes are processed.
1. Conditionals are evaluated.
