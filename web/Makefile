sources := $(wildcard *.markdown)
targets := $(patsubst %.markdown,%.html,$(sources))

asset_dir := .markdown
assets := $(wildcard $(asset_dir)/*)


all: $(targets)


%.html: %.markdown $(assets)
	if true; then \
		title=`echo "$<" | sed "s/\..*$$//g"`; \
		cat ${asset_dir}/top.html | sed "s/@@PAGETITLE@@/$$title/g" > "$@"; \
		\
		echo '<style type="text/css" media="screen">' >> "$@"; \
		if [ -f ".markdown/style.css" ]; then \
			cat ".markdown/style.css" >> "$@"; \
		else \
			cat ${asset_dir}/style.css >> "$@"; \
		fi; \
		echo '</style>' >> "$@"; \
		\
		cat ${asset_dir}/middle.html >> "$@"; \
		markdown < "$<" >> "$@"; \
		cat ${asset_dir}/bottom.html >> "$@"; \
		fi


clean:
	rm -f $(targets)

.PHONY: all clean
