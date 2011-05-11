# Get up and running with `delpy`


## Requirements

To run `delpy` you need:

* Python 2.5
* Borland Developer Studio 2006 (to trace and compile programs)
* [graphviz](http://www.graphviz.org/) (to produce graph diagrams)
* a pdf viewer (to view the diagrams)
* [wine](http://www.winehq.org/) (to run win32 binaries on Linux)


## Platform notes

`delpy` is developed and tested on three platforms:

* Windows native (native Delphi platform)
* Cygwin
* Linux (main development platform)
 
This means that wherever possible the code is all native Python, even at a 
performance loss.

Both the BDS 2006 compiler `DCC32.EXE` and the executables it produces
will generally run okay under `wine`, so it's possible to compile Delphi
programs in Linux and whenever this is attempted, `delpy` automatically
runs the compiler under `wine`.

The biggest obstacle to portability across platforms are path names, so
`delpy` will try hard to always pass relative paths to `DCC32.EXE`, but this
might fail if the compiler, the standard library, or the codebase, are either:

* on different Windows volumes (`c:`, `d:`)
* on different sides of a Cygwin mount boundary (outside of Cygwin's `/`)

For this very reason, `delpy` does not use the system BDS, but rather makes a
copy of it to be co-located with `delpy`. The best practice is thus:

* Keep `delpy` and your codebase on the same Windows volume
* Under Cygwin, keep `delpy` and your codebase inside the Cygwin root `/`,
for instance under `/home/myuser`


### Platform convention in this guide

The examples of uses in this guide do not keep a strong convention with
respect to which platform they are demonstrated on, because the result is
the same. The reader is expected to understand how to run the same command on
his platform.



## `delpy` on the PATH

It's a good idea to include `delpy` in your `PATH`, so that you only have to
type the name of the tool to run it, not the whole path. The examples in this
guide assume this to be the case.
