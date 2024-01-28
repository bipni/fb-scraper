from fb_scraper.exceptions import InvalidCookies
from fb_scraper.facebook_request import FacebookRequest
from fb_scraper.facebook_scraper import FacebookScraper
from fb_scraper.utils import parse_cookie_file

_request = FacebookRequest()
_scraper = FacebookScraper(_request)


def _set_cookies(filename: str):
    try:
        cookies = parse_cookie_file(filename)
    except ValueError as error:
        raise InvalidCookies(f'Cookies are in an invalid format: {error}') from error

    if cookies is not None:
        cookie_names = [c.name for c in cookies]

        missing_cookies = [c for c in ['c_user', 'xs'] if c not in cookie_names]

        if missing_cookies:
            raise InvalidCookies(f'Missing cookies with name(s): {missing_cookies}')

        _request.session.cookies.update(cookies)

        if not _request.is_logged_in():
            raise InvalidCookies('Cookies are not valid')


def get_group_posts_by_group_id(group_id: str, cookies: str, start_url: str = None):
    _set_cookies(cookies)

    return _scraper.get_group_posts_by_group_id(group_id, start_url)


def get_page_posts_by_page_id(page_id: str, cookies: str, start_url: str = None):
    _set_cookies(cookies)

    return _scraper.get_page_posts_by_page_id(page_id, start_url)
