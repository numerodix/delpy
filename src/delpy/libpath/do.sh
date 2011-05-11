#!/bin/bash
#
# Copyright: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

# delimit with |, this is a regex
excludes="lib|samples"

path_file="__path__.py"


action="$1";shift;

if [ -z "$action" ]; then
	echo "usage: $0 [dist|test]"
	echo
	echo " dist: (Re-)Deploy $path_file all over the tree, excluding: $excludes"
	echo " test: Run every *.py with python to check for ImportError"
	exit 1
fi


get_dir_list() {
	local dirs=

	for d in `find .. -type d | egrep -v "$excludes"`; do
		dirs="$d $dirs"
	done

	echo "$dirs"
}

do_dist() {
	local dirs=$(get_dir_list)
	for d in $dirs; do
		cp -v $path_file $d
	done
}

do_test() {
	local dirs=$(get_dir_list)
	for d in $dirs; do

		pys=$(ls $d/*.py | sort)
		for py in $pys; do

			local flag=
			local output=

			test=$(python $py 2>&1)
			# this is fragile, only checks for ImportError
			if echo "$test" | grep ImportError &>/dev/null; then
				flag="-"
			else
				flag="+"
			fi

			[ -n "$test" ] && output="<non-empty-output>"
			
			printf "%s %-34s %s\n" "$flag" "$py" "$output"
		done
	done
}


if [ "$action" = "dist" ]; then
	do_dist
elif [ "$action" = "test" ]; then
	do_test
fi
