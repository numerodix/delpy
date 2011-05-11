`delpy` is a collection of Python tools for working with legacy Delphi
codebases.

With `delpy` you can:

* Explore an unknown codebase and discover what it contains.
* Visualize a program as a graph showing all the files it includes and how
  they depend on each other.
* Compile a program/library outside of the IDE (reproducable automated builds 
that can be run on your build server).
* Preprocess a codebase to get rid of preprocessor statements.
* Prune the codebase removing all files not part of the source of any program.
* Prettify source code.

`delpy` has been tested against 6 million lines of code written with Borland Developer
Studio 2006. If you compile your program with a different version of
Delphi, your mileage may vary.

`delpy` was written by Martin Matusiak in 2010 and is a by-product of my
master's thesis at Utrecht University.

* [Download](https://sourceforge.net/projects/delpysuite/files)

## To begin with

* [Get up and running with delpy](up_and_running.html)
* [The basics of Delphi programs](program_basics.html)

## Tools

* [compilertools.py](compilertools.html) - Setting up a local BDS
* [viewgraph.py](viewgraph.html) - Tracing programs and viewing the program graph
* [explore_codebase.py](explore_codebase.html) - Exploring a codebase
* [graphdiff.py](graphdiff.html) - Comparing graphs
* [makedelphi.py](makedelphi.html) - Compiling Delphi programs
* [preprocess.py](preprocess.html) - Preprocessing a codebase
* [prunecodebase.py](prunecodebase.html) - Pruning a codebase
* [delphiparser.py](delphiparser.html) - Prettifying source code

## Advanced uses

`delpy` is not only a tool suite, but also a full blown program transformation
framework.

* [The parser](parser.html)
* [The grammar](grammar.html)
