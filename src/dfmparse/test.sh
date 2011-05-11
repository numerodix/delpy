#!/bin/bash
#
# Copyright: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

path="$1"; shift;
if [ -z "$path" ]; then
	echo "Usage: $0 <path>"
	exit
fi


fs=$(find "$path" -type f -iname '*.dfm' -print)

IFS=$'\n'
for f in $fs; do
	if $(file "$f" | grep "text" &>/dev/null); then
		python parsedfm.py "$f"
		if [ $? != 0 ]; then
			echo ">>> ERROR : $f"
		else
			echo ">>> PASSED: $f"
		fi
	fi
done
