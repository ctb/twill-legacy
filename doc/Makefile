all: index.html commands.html developer.html python-api.html testing.html \
     other.html browsing.html examples.html extensions.html install.html

%.html : %.txt
	rst2html.py --stylesheet=default.css $< $@
