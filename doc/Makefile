all: browsing.html changelog.html commands.html developer.html \
     examples.html extensions.html index.html install.html \
     other.html  python-api.html testing.html

%.html : %.txt
	rst2html.py --stylesheet=default.css $< $@
