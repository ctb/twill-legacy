from time import sleep

import pytest
from httpx import ReadTimeout
from twill import commands


def test(url: str):
    commands.reset_browser()
    commands.go(url)
    commands.go("/sleep")
    commands.find("sorry for the delay")
    commands.timeout(0.25)  # do not wait for server
    with pytest.raises(ReadTimeout):
        commands.go("/sleep")
    sleep(0.25)  # now wait for server to catch up
    commands.timeout(900)
    commands.timeout(10)
    commands.timeout(0)
    commands.timeout()
    commands.reset_browser(url)
    commands.go(url)
