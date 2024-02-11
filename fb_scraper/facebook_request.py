import random
import time
import warnings

from errorify import errorify
from requests import RequestException
from requests_html import HTMLSession

from fb_scraper.constants import DEFAULT_REQUESTS_TIMEOUT, FB_MBASIC_BASE_URL
from fb_scraper.exceptions import (
    AccountDisabled,
    InvalidCookies,
    LoginRequired,
    NotFound,
    RottenCookies,
    TemporarilyBanned,
    UnexpectedResponse,
)
from fb_scraper.facebook_constants import (
    DEFAULT_HEADERS,
    NOT_FOUND_TITLES,
    TEMP_BAN_TITLES,
)
from fb_scraper.utils import parse_cookie_file


class FacebookRequest:
    base_url = FB_MBASIC_BASE_URL

    default_headers = DEFAULT_HEADERS

    have_checked_locale = False

    def __init__(self, cookies: list[str], session=None, requests_kwargs=None) -> None:
        if session is None:
            session = HTMLSession()
            session.headers.update(self.default_headers)

        if requests_kwargs is None:
            requests_kwargs = {
                'timeout': DEFAULT_REQUESTS_TIMEOUT
            }

        self.cookies = cookies
        self.session = session
        self.requests_kwargs = requests_kwargs
        self.request_count = 0
        self._warning()

    def _warning(self):
        if len(self.cookies) < 10:
            warnings.warn('Use at least 10 cookies')

    def set_user_agent(self, user_agent):
        self.session.headers['User-Agent'] = user_agent

    def set_cookies(self, filename: str):
        try:
            cookies = parse_cookie_file(filename)
        except ValueError as error:
            try:
                print(errorify(error))
                raise InvalidCookies(f'Cookies are in an invalid format: {error}') from error
            except InvalidCookies as e:
                print(errorify(e))
                return False

        if cookies is not None:
            cookie_names = [c.name for c in cookies]

            missing_cookies = [c for c in ['c_user', 'xs'] if c not in cookie_names]

            if missing_cookies:
                try:
                    raise InvalidCookies(f'Missing cookies with name(s): {missing_cookies}')
                except InvalidCookies as e:
                    print(errorify(e))
                    return False

            self.session.cookies.update(cookies)

            if not self.is_logged_in():
                try:
                    raise InvalidCookies('Cookies are not valid')
                except InvalidCookies as e:
                    print(errorify(e))
                    return False

            return True

        return False

    def is_logged_in(self) -> bool:
        try:
            url = self.base_url + '/settings'

            response = self.session.get(url=url, **self.requests_kwargs)

            response.html.html = response.html.html.replace('<!--', '').replace('-->', '')
            response.raise_for_status()

            title = response.html.find('title', first=True)

            if title:
                if title.text.lower() in NOT_FOUND_TITLES:
                    raise NotFound(title.text)

                if title.text.lower() == "error":
                    raise UnexpectedResponse("Your request couldn't be processed")

                if title.text.lower() in TEMP_BAN_TITLES:
                    raise TemporarilyBanned(title.text)

                if ">your account has been disabled<" in response.html.html.lower():
                    raise AccountDisabled("Your Account Has Been Disabled")

                if ">We saw unusual activity on your account. This may mean that someone has used your account without your knowledge.<" in response.html.html:
                    raise AccountDisabled("Your Account Has Been Locked")

                if (title.text == "Log in to Facebook | Facebook" or response.url.startswith(self.base_url + '/login')):
                    raise LoginRequired("A login (cookies) is required to see this page")

            return True
        except LoginRequired:
            return False

    def get(self, url, **kwargs):
        try:
            interval = random.randint(0, 11)
            time.sleep(interval)

            if len(self.cookies) == 0:
                raise RottenCookies('All Cookies are Rotten')

            scrape_type = kwargs.get('scrape_type', None)

            if scrape_type != 'reply':
                cookie_index = self.request_count % len(self.cookies)
                cookie_file = f'cookies/{self.cookies[cookie_index]}'
                self.request_count += 1

                print(f'Cookie Using: {cookie_file}')

                cookie_status = self.set_cookies(cookie_file)

                if not cookie_status:
                    print(f'Removing Cookie: {self.cookies[cookie_index]}')
                    self.cookies.pop(cookie_index)
                    self.get(url, **kwargs)

            url = str(url)

            response = self.session.get(url=url, **self.requests_kwargs)

            response.html.html = response.html.html.replace('<!--', '').replace('-->', '')
            response.raise_for_status()

            title = response.html.find('title', first=True)

            if title:
                if title.text.lower() in NOT_FOUND_TITLES:
                    raise NotFound(title.text)

                if title.text.lower() == "error":
                    raise UnexpectedResponse("Your request couldn't be processed")

                if title.text.lower() in TEMP_BAN_TITLES:
                    try:
                        raise TemporarilyBanned(title.text)
                    except TemporarilyBanned as e:
                        print(errorify(e))
                        print(f'Removing Cookie: {self.cookies[cookie_index]}')
                        self.cookies.pop(cookie_index)
                        self.get(url, **kwargs)

                if ">your account has been disabled<" in response.html.html.lower():
                    try:
                        raise AccountDisabled("Your Account Has Been Disabled")
                    except AccountDisabled as e:
                        print(errorify(e))
                        print(f'Removing Cookie: {self.cookies[cookie_index]}')
                        self.cookies.pop(cookie_index)
                        self.get(url, **kwargs)

                if ">We saw unusual activity on your account. This may mean that someone has used your account without your knowledge.<" in response.html.html:
                    try:
                        raise AccountDisabled("Your Account Has Been Locked")
                    except AccountDisabled as e:
                        print(errorify(e))
                        print(f'Removing Cookie: {self.cookies[cookie_index]}')
                        self.cookies.pop(cookie_index)
                        self.get(url, **kwargs)

                if (title.text == "Log in to Facebook | Facebook" or response.url.startswith(self.base_url + '/login')):
                    try:
                        raise LoginRequired("A login (cookies) is required to see this page")
                    except LoginRequired as e:
                        print(errorify(e))
                        print(f'Removing Cookie: {self.cookies[cookie_index]}')
                        self.cookies.pop(cookie_index)
                        self.get(url, **kwargs)

            return response.html.html
        except RequestException as error:
            print('Exception while requesting URL: %s\nException: %r', url, error)
            raise
