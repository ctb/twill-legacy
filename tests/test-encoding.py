import twilltestlib
import mechanize
from cStringIO import StringIO

def test_form_parse():
    content = "&rsaquo;"
    fp = StringIO(content)

    # latin-1...
    mechanize.ParseFile(fp, "<test-encoding.py fp>", encoding='latin-1',
						backwards_compat=False)
