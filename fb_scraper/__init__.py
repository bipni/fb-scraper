import json
import locale
import logging
import os
import pathlib
import pickle
import re
import sys
import time
import traceback
import warnings
from datetime import datetime, timedelta
from typing import Any, Dict, Iterator, Optional, Set, Union

from requests.cookies import cookiejar_from_dict

from fb_scraper.exceptions import InvalidCookies
from fb_scraper.facebook_scraper import FacebookScraper
from fb_scraper.utils import parse_cookie_file

_scraper = FacebookScraper()


def set_cookies(filename: str):
    try:
        cookies = parse_cookie_file(filename)
    except ValueError as error:
        raise InvalidCookies(f'Cookies are in an invalid format: {error}') from error

    if cookies is not None:
        cookie_names = [c.name for c in cookies]

        missing_cookies = [c for c in ['c_user', 'xs'] if c not in cookie_names]

        if missing_cookies:
            raise InvalidCookies(f'Missing cookies with name(s): {missing_cookies}')

        _scraper.session.cookies.update(cookies)

        if not _scraper.is_logged_in():
            raise InvalidCookies('Cookies are not valid')


def get_group_posts_by_group_id(group_id: str, cookies: str, start_url: str = None):
    set_cookies(cookies)

    return _scraper.get_group_posts_by_group_id(group_id, start_url)
