# Prune a codebase

A codebase, especially one with a long history, tends to accumulate various
obsolete files like cache files written by various tools and source code files
that have been obsoleted or saved "just in case" and forgotten. In these cases
it might seem like there are files around that are obsolete, but it's not
clear which ones are safe to remove.

What we can do is compute all the program graphs in the codebase and check for
files that don't belong to any of the graphs. This, however, requires a fully
accurate program graph, which means the codebase first has to be 
[preprocessed](preprocess.html).


## A pruning example

We start with a codebase:

	$ find treetest/ | sort
	treetest/
	treetest/Lib
	treetest/Lib/Lib.pas
	treetest/Src
	treetest/Src/MainWindow.dfm
	treetest/Src/MainWindow.pas
	treetest/Src/Module.pas
	treetest/Src/Project
	treetest/Src/Project/Flagship.bdsproj
	treetest/Src/Project/Flagship.bdsproj.local
	treetest/Src/Project/Flagship.cfg
	treetest/Src/Project/Flagship.dpr
	treetest/Src/Project/Flagship.identcache
	treetest/Src/Project/Flagship.res
	treetest/Src/Project/Sideshow.bdsproj
	treetest/Src/Project/Sideshow.bdsproj.local
	treetest/Src/Project/Sideshow.cfg
	treetest/Src/Project/Sideshow.dpr
	treetest/Src/Project/Sideshow.identcache
	treetest/Src/Project/Sideshow.res
	treetest/Src/SideWindow.dfm
	treetest/Src/SideWindow.pas

We find the program graphs it contains:

	$ explore_codebase.py treetest/ -t
	Graphs:
	= treetest/Src/Project/Flagship.bdsproj =
	-- treetest/Src/Project/Flagship.dpr
	= treetest/Src/Project/Sideshow.bdsproj =
	-- treetest/Src/Project/Sideshow.dpr

Okay, there are two. We trace the programs:

	$ viewgraph.py treetest/Src/Project/Flagship.bdsproj -q
	...
	* Wrote file /tmp/.Flagship.bdsproj.graph . ...

	$ viewgraph.py treetest/Src/Project/Sideshow.bdsproj -q
	...
	* Wrote file /tmp/.Sideshow.bdsproj.graph . ...

### Prune with respect to both program graphs

Now we can prune the codebase with the respect to these two programs:

	$ prunecodebase.py /tmp/.Flagship.bdsproj.graph /tmp/.Sideshow.bdsproj.graph
	DELETE: Flagship.bdsproj.local
	DELETE: Flagship.identcache
	DELETE: Sideshow.bdsproj.local
	DELETE: Sideshow.identcache

We can verify that no necessary files were removed by compiling the programs:

	$ makedelphi.py /tmp/.Flagship.bdsproj.graph
	$ makedelphi.py /tmp/.Sideshow.bdsproj.graph

### Prune with respect to one of the program graphs

We could also prune with respect to just one of the programs, as a way to
isolate the sources of `treetest/Src/Project/Flagship.bdsproj` from those of
`treetest/Src/Project/Sideshow.bdsproj`:

	$ prunecodebase.py /tmp/.Flagship.bdsproj.graph
	DELETE: Flagship.bdsproj.local
	DELETE: Flagship.identcache
	DELETE: Sideshow.bdsproj
	DELETE: Sideshow.bdsproj.local
	DELETE: Sideshow.cfg
	DELETE: Sideshow.dpr
	DELETE: Sideshow.identcache
	DELETE: Sideshow.res

We should then check that the program compiles:

	$ makedelphi.py /tmp/.Flagship.bdsproj.graph
