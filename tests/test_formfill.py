from .utils import execute_script


def test(url: str):
    """Test the 'formfill' extension stuff."""
    execute_script("test_formfill.twill", initial_url=url)
