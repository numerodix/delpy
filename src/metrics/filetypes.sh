#!/bin/bash
#
# Copyright: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.


find -type f \
	| grep -v .git \
	| sed "s/.*\(\..*\)$/\1/g" \
	| tr '[:upper:]' '[:lower:]' \
	| sort \
	| uniq -c \
	| sort -n
