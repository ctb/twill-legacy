import os

from twill.utils import gather_filenames


def test_gather_dir():
    this_dir = os.path.dirname(__file__)
    test_gather = os.path.join(this_dir, 'test_gather')
    cwd = os.getcwd()

    os.chdir(test_gather)
    try:
        files = gather_filenames(('.',))
        if os.sep != '/':
            files = [f.replace(os.sep, '/') for f in files]
        assert sorted(files) == sorted([
            './00-testme/x-script.twill',
            './01-test/b.twill', './02-test2/c.twill',
            './02-test2/02-subtest/d.twill']), files
    finally:
        os.chdir(cwd)
