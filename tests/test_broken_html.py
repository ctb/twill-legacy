from twill import commands


def test_links_parsing(url):
    """Test parsing a link text inside a span."""
    commands.go('/broken_linktext')
    # make sure link text is found even if it is nested
    commands.follow('some text')


def test_fixing_forms(url):
    """Test parsing of broken HTML forms."""
    forms = commands.get_browser().get_all_forms

    commands.go(url)

    commands.go('/broken_form_1')
    assert len(forms()) == 1, 'can fix form 1'

    commands.go('/broken_form_2')
    assert len(forms()) == 1, 'can fix form 2'

    commands.go('/broken_form_3')
    assert len(forms()) == 1, 'can fix form 3'

    commands.go('/broken_form_4')
    assert len(forms()) == 2, 'can fix form 4'

    commands.go('/broken_form_5')
    assert len(forms()) == 1, 'can fix form 5'

    assert set(forms()[0].inputs.keys()) == set(
        'username password login'.split()), 'should get proper fields'
