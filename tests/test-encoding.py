import twilltestlib
from _mechanize_dist import ClientForm
from cStringIO import StringIO

def test_form_parse():
    content = "&rsaquo;"
    fp = StringIO(content)

    # latin-1...
    ClientForm.ParseFile(fp, "<test-encoding.py fp>", encoding='latin-1',
                         backwards_compat=False)
