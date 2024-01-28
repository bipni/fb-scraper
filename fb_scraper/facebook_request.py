from requests import RequestException
from requests_html import HTMLSession

from fb_scraper.constants import DEFAULT_REQUESTS_TIMEOUT, FB_MBASIC_BASE_URL
from fb_scraper.exceptions import (  # InvalidCookies,; LoginError,
    AccountDisabled,
    LoginRequired,
    NotFound,
    TemporarilyBanned,
    UnexpectedResponse,
)
from fb_scraper.facebook_constants import (
    DEFAULT_HEADERS,
    NOT_FOUND_TITLES,
    TEMP_BAN_TITLES,
)


class FacebookRequest:
    base_url = FB_MBASIC_BASE_URL

    default_headers = DEFAULT_HEADERS

    have_checked_locale = False

    def __init__(self, session=None, requests_kwargs=None) -> None:
        if session is None:
            session = HTMLSession()
            session.headers.update(self.default_headers)

        if requests_kwargs is None:
            requests_kwargs = {
                'timeout': DEFAULT_REQUESTS_TIMEOUT
            }

        self.session = session
        self.requests_kwargs = requests_kwargs
        self.request_count = 0

    def set_user_agent(self, user_agent):
        self.session.headers['User-Agent'] = user_agent

    def is_logged_in(self) -> bool:
        try:
            self.get(self.base_url + '/settings')
            return True
        except LoginRequired:
            return False

    def get(self, url, **kwargs):
        try:
            self.request_count += 1

            url = str(url)

            if kwargs.get('post'):
                kwargs.pop('post')
                response = self.session.post(url=url, **kwargs)
            else:
                response = self.session.get(url=url, **self.requests_kwargs, **kwargs)

            response.html.html = response.html.html.replace('<!--', '').replace('-->', '')
            response.raise_for_status()

            title = response.html.find('title', first=True)

            if title:
                if title.text.lower() in NOT_FOUND_TITLES:
                    raise NotFound(title.text)
                elif title.text.lower() == "error":
                    raise UnexpectedResponse("Your request couldn't be processed")
                elif title.text.lower() in TEMP_BAN_TITLES:
                    raise TemporarilyBanned(title.text)
                elif ">your account has been disabled<" in response.html.html.lower():
                    raise AccountDisabled("Your Account Has Been Disabled")
                elif ">We saw unusual activity on your account. This may mean that someone has used your account without your knowledge.<" in response.html.html:
                    raise AccountDisabled("Your Account Has Been Locked")
                elif (title.text == "Log in to Facebook | Facebook" or response.url.startswith(self.base_url + '/login')):
                    raise LoginRequired("A login (cookies) is required to see this page")

            return response.html.html
        except RequestException as error:
            print('Exception while requesting URL: %s\nException: %r', url, error)
            raise
