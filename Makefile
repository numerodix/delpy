web:
	rsync -avP --delete -e ssh web/ numerodix,delpysuite@web.sourceforge.net:htdocs/


.PHONY: web
