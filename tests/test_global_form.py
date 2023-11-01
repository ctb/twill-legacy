from io import StringIO

from .utils import execute_script


def test(url: str, output: StringIO):
    execute_script("test_global_form.twill", initial_url=url)
    out = output.getvalue()
    assert "Form #1" in out
    assert "Form name=login (#2)" in out
    assert "Form name=login (#3)" in out
