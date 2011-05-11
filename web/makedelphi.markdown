# Compiling Delphi programs

Compiling a Delphi program happens in two steps. First trace the program (you
can use the `-q` option to skip viewing the graph):

	$ viewgraph.py PriceCheck.dpr -q
	...
	* Wrote file /tmp/.PriceCheck.dpr.graph . ...

Now run the `makedelphi.py` tool on the graph (the `-t` parameter indicates
the location where the executable will be written):

	$ makedelphi.py /tmp/.PriceCheck.dpr.graph -t .
	>> Convert Gui.dfm to binary dfm format ...
	 [/home/frank/code/samples/pricecheck] + wine \
		../../dfmconvert/dfmconvert.exe --to-binary Gui.dfm --output Gui.dfm.bin
	> Converting from text to binary: Gui.dfm -> Gui.dfm.bin
	* DONE ...
	>> Building PriceCheck.dpr ...
	 [/home/frank/code/samples/pricecheck] + wine \
		../../dcc32/bin/DCC32.EXE -u"../../dcc32/lib;../../dcc32/lib/Indy9" \
		-E"." -N"/tmp" -LE"/tmp" -LN"/tmp" PriceCheck.dpr
	Borland Delphi for Win32 compiler version 18.0
	Copyright (c) 1983,2005 Borland Software Corporation
	Core.pas(143)
	SocketTypes.pas(146)
	SocketMarshall.pas(200)
	SocketInfo.pas(13)
	SocketClient.pas(178)
	Gui.pas(133)
	PriceCheck.dpr(14)
	834 lines, 0.45 seconds, 398592 bytes code, 23272 bytes data.
	* DONE ...

There are two things happening here. 

First all of, the `Form`s in the program
are converted from a text format to a binary format. This is necessary,
otherwise the `DCC32.EXE` compiler is not able to link them into the
executable. So `makedelphi.py` executes `dfmconvert.exe` to convert `Gui.dfm`.
This conversion is only for the benefit of the compiler and the files are
reverted afterwards, so no permanent change is made to the codebase.

Then, `makedelphi.exe` executes the Delphi compiler `DCC32.EXE` with the
`Program` as argument, here `PriceCheck.dpr`. The `-u` option tells the
compiler where the sources are to be found, and here both the path to the
standard library as well as any additional search paths of the program must be
included. The paths are relative for portability.

Tracing the program before compilation is necessary to discover all of the
paths necessary for compilation and to find all of the program's `Form`s.

You should make sure that you compile the program on the same platform that
you trace it on, otherwise the paths will not agree and compilation will
probably fail.
