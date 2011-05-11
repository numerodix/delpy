#!/bin/bash
#
# Copyright: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

codebase="$1";shift;

if [ -z "$codebase" ]; then
	echo "Usage:  $0 <dir>"
	exit 1
fi

src_files=".*\.(pas|dpr|dpk|inc|dfm|h|hpp|c|cpp|hxx)"
build_target_files=".*\.(bdsproj)"


format() {
	local n="$1";shift;
	local len=${#n}
	local steps=$(( $len / 3 ))
	local fn=
	for i in $(seq 1 $steps); do
		local pos=$(( $len - ($i * 3) ))
		fn=",${n:$pos:3}$fn"
	done
	local prefix=$(( $len - ($steps * 3) ))
	local fn="${n:0:$prefix}$fn"
	fn=$(echo "$fn" | sed "s/^,//g")
	echo "$fn"
}

factor() {
	local n="$1";shift;
	local m=
	local unit=0
	while (( $n > 1023 )); do
		m=$(( $n % 1024 ));
		n=$(( $n / 1024 ));
		unit=$(( $unit + 1 ))
	done
	if (( $unit == 0 )); then
		unit="b"
	elif (( $unit == 1 )); then
		unit="kb"
	elif (( $unit == 2 )); then
		unit="mb"
	elif (( $unit == 3 )); then
		unit="gb"
	fi

	# prefix with zeros
	if [ "$m" ]; then
		while (( ${#m} < 3 )); do
			m="0$m"
		done
	fi

	# assemble and truncate to 3 significant figures
	local num="$n"
	if [ "$m" ]; then
		local digits="$n$m"
		if [ ${#digits} -gt 3 ]; then
			local dx=$(( ${#digits} - 3 ))
			local index=$(( ${#m} - $dx ))
			m=${m::$index}
		fi
		local num="$n"
		[ "$m" ] && num="$n.$m"
	fi

	echo "$num$unit"
}

disable_dotgit() {
	if [ -d $codebase/.git ]; then
		echo " ==> Disabling $codebase/.git (compress first)"
		(cd $codebase && git gc)
		mv $codebase/.git /tmp
	fi
}

enable_dotgit() {
	if [ -d /tmp/.git ]; then
		echo " ==> Enabling $codebase/.git"
		mv /tmp/.git $codebase
	fi
}

#echo $(factor 3)
#echo $(factor 23)
#echo $(factor 123)
#echo $(factor 4123)
#echo $(factor 34123)
#echo $(factor 934123)
#echo $(factor 2934123)
#echo $(factor 22934123)
#echo $(factor 322934123)
#echo $(factor 4322934123)
#echo $(factor 24322934123)
#echo $(factor 2157436928)
#echo $(format 3)
#echo $(format 23)
#echo $(format 123)
#echo $(format 4123)
#echo $(format 34123)
#echo $(format 934123)
#echo $(format 2934123)
#echo $(format 22934123)
#echo $(format 322934123)
#echo $(format 4322934123)
#echo $(format 24322934123)
#exit

disable_dotgit

du_size=$(du -s --block-size=1 "$codebase" | awk '{print $1}')
find_size=$(find -type f -exec cat {} \; | wc | awk '{print $3}')
build_target_file_count=$(find "$codebase" -type f -regextype posix-egrep -iregex "$build_target_files" | wc -l)
src_file_count=$(find "$codebase" -type f -regextype posix-egrep -iregex "$src_files" | wc -l)
wc_count=$(find "$codebase" -type f -regextype posix-egrep -iregex "$src_files" -exec cat {} \; | wc)
line_count=$(echo "$wc_count" | awk '{print $1}')
byte_count=$(echo "$wc_count" | awk '{print $3}')

enable_dotgit

echo ">>> $codebase"
echo "  - Codebase size du  : $(factor $du_size)"
echo "  - Codebase size find: $(factor $find_size)"
echo "* Source files:"
echo "  - Build targets: $(format $build_target_file_count)"
echo "  - Souce files  : $(format $src_file_count)"
echo "  - Souce lines  : $(format $line_count)"
echo "  - Souce bytes  : $(factor $byte_count)"

echo
echo
echo "|-"
echo "! align=left  | $codebase"
echo "| align=right | $(factor $du_size)"
echo "| align=right | $(format $build_target_file_count)"
echo "| align=right | $(format $src_file_count)"
echo "| align=right | $(format $line_count)"
echo "| align=right | $(factor $byte_count)"
