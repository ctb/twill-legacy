from .utils import execute_script


def test(url, out):
    execute_script('test_global_form.twill', initial_url=url)
    out = out.getvalue()
    assert "Form #1" in out
    assert "Form name=login (#2)" in out
    assert "Form name=login (#3)" in out
