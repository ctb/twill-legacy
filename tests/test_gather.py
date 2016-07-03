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
        assert files == [
            './00-testme/x-script',
            './01-test/a', './01-test/b', './02-test2/c'], files
    finally:
        os.chdir(cwd)
