# Setting up a local BDS

Before it can trace and compile programs, `delpy` needs a copy of BDS 2006
(actually a subset of it) that it will co-locate with itself. So the directory
structure needs to be:

	delpy/
	dcc32/

where `dcc32` contains the files from BDS. The tool `compilertools.py` will do
this for you. Run the tool to see if this has been done already:

	C:\code\delpy> compilertools.py
	! Missing: C:\code\dcc32\bin\DCC32.EXE ...
	! Missing: C:\code\dcc32\bin\borlndmm.dll ...
	! Missing: C:\code\dcc32\bin\rlink32.dll ...
	! Missing: C:\code\dcc32\lib ...
	! Missing: C:\code\dcc32\src ...
	Files needed from the Borland Delphi distribution (on path ${BDS}), to be
	placed in directories under the base directory (C:\code\dcc32):

	${BDS}\Bin\DCC32.EXE                 ->  C:\code\dcc32\bin\DCC32.EXE
	${BDS}\Bin\borlndmm.dll              ->  C:\code\dcc32\bin\borlndmm.dll
	${BDS}\Bin\rlink32.dll               ->  C:\code\dcc32\bin\rlink32.dll
	${BDS}\lib\**                        ->  C:\code\dcc32\lib\**
	${BDS}\source\**                     ->  C:\code\dcc32\src\**

	To install the missing tools:
	 C:\code\delpy\compilertools.py ${BDS}

To perform the copy run the tool with the path to where BDS is installed.

	C:\code\delpy> compilertools.py C:\Program Files\Borland\BDS\4.0

The same under Cygwin:

	$ compilertools.py /cygwin/c/Program\ Files/Borland/BDS/4.0

If you're doing this under Linux and you're wondering how to access the files
from Windows, you can do this over a virtual machine shared folder, for example.

To confirm that everything worked correctly run the tool again without
arguments. If it outputs nothing then everything is in order.

	C:\code\delpy> compilertools.py
