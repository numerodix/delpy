# The basics of Delphi programs

Delphi programs (strictly speaking, BDS 2006 programs) are composed of many
different types of files.


## The ingredients of a program

An item in the list that has a nested item participates in a source-to-product
relationship, so a `Unit` contains source code and is compiled to a `CompiledUnit`,
which contains the corresponding binary code.

* `DelphiProjectGroup (.bdsgroup)` - a grouping of `DelphiProject`s
* `DelphiProject (.bdsproj)` - a project definition, points to one of
  `Program`/`Library`/`Package`
* `DelphiCompilerFlags (.cfg)` - contains the flags passed to `DCC32.EXE`
* `Program (.dpr)` - a program entry point for an executable program
	1. `CompiledProgram (.exe)`
* `Library (.dpr)` - a program entry point for a dynamically linked library
	1. `CompiledLibrary (.dll)`
* `Package (.dpk)` - a program entry point for a special library
	1. `CompiledPackage (.bpl, .dcp)`
	1. `CompiledControlPanel (.cpl)`
	1. `CompiledActiveXControl (.ocx)`
* `Unit (.pas)` - a source code module
	1. `CompiledUnit (.dcu)`
* `Form (.dfm)` - contains the definition of a gui form
* `Resource (.res, .*)` - a binary resource (not code), like the program icon
* `FileInclude (.inc)` - source code snippet included into the current file
* `BinaryObject (.obj)` - binary code that can be linked into a Delphi program

The full definition is found in `delpy/model.py`.


## The composition of a program

The source code of a Delphi program is composed of:

1. One `Program` (alternatively, a `Library` or `Package`)
1. Some number of `Unit`s
1. Some number of `Form`s
1. Some number of `Resource`s
1. Some number of `BinaryObject`s (less common)

The `Program` file contains the source code executed immediately upon running
the program, and `Unit`s contain additional source code. 

To compile a program, then, we need to:

1. Compile all of the `Unit`s (written to disk as intermediate `CompiledUnit`
   files),
1. Compile the `Program` file, and
1. Link all of the above along with the `Form`s, `Resource`s and
   `BinaryObject`s into a `CompiledProgram`.

However, in all but trivial cases there is also a `DelphiProject`
file, which contains crucial metadata used in compilation, such as:

1. Compiler and linker flags (duplicated in `DelphiCompilerFlags`)
1. Preprocessor symbols
1. Search paths for additional units (source or binary)
1. Various other parameters, such as where to output the `CompiledProgram`, where to
   output the `CompiledUnit`s etc.


## A program graph

A program graph is a graph that contains all the sources
(whether source code, or binary files like `Resource`s) of a program.
The root of the graph is either the program entry point (`Program`/`Library`/`Package`),
which refers to `Unit`s (which in turn refer to more `Unit`s and so on) or a
`DelphiProject` (if present).

![A program graph](imgs/pricecheck_resources.png)

Here we see the graph of a simple program. The program has one form
(`Gui.dfm`), one resource file (`PriceCheck.res`) and six `Unit`s. 

The arrows represent a dependency relationship, so in order to compile
`SocketMarshall.pas` you first need to compile `SocketTypes.pas`.
