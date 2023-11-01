import os
from pathlib import Path

from twill.utils import gather_filenames


def test_gather_dir():
    test_dir = Path(__file__).parent / "test_gather"
    cwd = Path.cwd()

    os.chdir(test_dir)
    try:
        files = gather_filenames((".",))
        if os.sep != "/":
            files = [f.replace(os.sep, "/") for f in files]
        assert sorted(files) == sorted(
            (
                "./00-testme/x-script.twill",
                "./01-test/b.twill",
                "./02-test2/c.twill",
                "./02-test2/02-subtest/d.twill",
            )
        ), files
    finally:
        os.chdir(cwd)
