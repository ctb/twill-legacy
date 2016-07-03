
from cStringIO import StringIO

from _mechanize_dist import ClientForm


def test_form_parse():
    content = "&rsaquo;"
    fp = StringIO(content)

    # latin-1...
    ClientForm.ParseFile(fp, "<test_encoding.py fp>", encoding='latin-1',
                         backwards_compat=False)
