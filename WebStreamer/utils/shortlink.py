from pyshorteners import Shortener
from random import choice


def shorten_link(url: str) -> str:
    """
    Shorten the given url with shortlink.org
    """
    s = Shortener()
    rand_url = choice([s.isgd.short, s.dagd.short])
    return rand_url(url)
