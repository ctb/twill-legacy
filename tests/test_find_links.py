import twill
from twill import commands
from twill.utils import Link


def test(url: str):
    commands.reset_browser()
    browser = twill.browser
    commands.go(url)

    link = browser.find_link("logout")
    assert isinstance(link, Link)
    assert link == ("log out", "logout")

    link = browser.find_link("log out")
    assert isinstance(link, Link)
    assert link == ("log out", "logout")

    link = browser.find_link("log ?out")
    assert isinstance(link, Link)
    assert link == ("log out", "logout")

    assert browser.find_link("log off") is None

    assert browser.find_link("Logout") is None

    link = browser.find_link("test.*")
    assert isinstance(link, Link)
    assert link == ("test spaces", "test spaces")

    links = browser.find_links("logout")
    assert all(isinstance(link, Link) for link in links)
    assert links == [("log out", "logout")]

    links = browser.find_links("log out")
    assert all(isinstance(link, Link) for link in links)
    assert links == [("log out", "logout")]

    links = browser.find_links("log? out")
    assert all(isinstance(link, Link) for link in links)
    assert links == [("log out", "logout")]

    assert browser.find_links("log off") == []

    assert browser.find_links("Logout") == []

    links = browser.find_links("test.*")
    assert all(isinstance(link, Link) for link in links)
    assert links == [
        ("test spaces", "test spaces"),
        ("test spaces2", "test_spaces"),
    ]

    links = browser.find_links(".*")
    assert all(isinstance(link, Link) for link in links)
    assert len(links) == 5
