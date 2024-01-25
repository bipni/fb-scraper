from bs4 import BeautifulSoup
from requests import RequestException
from requests_html import HTMLSession

from fb_scraper.constants import DEFAULT_REQUESTS_TIMEOUT, FB_MBASIC_BASE_URL
from fb_scraper.error_handler import error_handler
from fb_scraper.exceptions import (  # InvalidCookies,; LoginError,
    AccountDisabled,
    LoginRequired,
    NotFound,
    TemporarilyBanned,
    UnexpectedResponse,
)
from fb_scraper.extractors import Extractors
from fb_scraper.facebook_constants import (
    DEFAULT_HEADERS,
    NOT_FOUND_TITLES,
    TEMP_BAN_TITLES,
)


class FacebookScraper:
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
            print('Logged In')
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

    def get_group_posts_by_group_id(self, group_id: str, start_url: str = None):
        try:
            group_posts = []
            group_post = {}
            url = FB_MBASIC_BASE_URL + '/groups' + f'/{group_id}'

            # if start_url, then scrape from start_url
            if start_url is not None:
                url = start_url

            # get the html response from facebook
            page_response = self.get(url)

            # parse html
            soup = BeautifulSoup(page_response, 'html.parser')

            # article tag contains the post
            posts = soup.find_all('article')

            if posts:
                extractors = Extractors()

                for post in posts:
                    print('New Post')

                    # get all link contents
                    link_contents = post.find_all('a')

                    for i, link_content in enumerate(link_contents):
                        # first link content contains the information of user
                        if i == 0:
                            group_post['profile_id'] = extractors.profile_id(link_content)
                            group_post['profile_name'] = extractors.profile_name(link_content)
                            group_post['profile_url'] = extractors.profile_url(link_content)

                        # link content that contains 'Full Story' text has post url
                        if link_content.get_text(strip=True) == 'Full Story':
                            group_post['post_id'] = extractors.post_id(link_content)
                            group_post['post_url'] = extractors.post_url(link_content)

                    # get all span contents
                    span_contents = post.find_all('span')

                    for i, span_content in enumerate(span_contents):
                        # third span content contains the post text
                        if i == 2:
                            group_post['post_text'] = extractors.post_text(span_content)

                    if group_post['post_url']:
                        comments = []

                        post_response = self.get(group_post['post_url'])

                        soup = BeautifulSoup(post_response, 'html.parser')

                        # if class 'ea' and id exist, then those will be comments
                        comment_contents = soup.find_all('div', {'class': 'ea', 'id': True})

                        for comment_content in comment_contents:
                            comment = {}
                            comment['comment_id'] = extractors.comment_id(comment_content)
                            comment['comment_text'] = extractors.comment_text(comment_content)
                            comments.append(comment)

                    group_post['comments'] = comments

                    group_posts.append(group_post)
                    group_post = {}

            print(group_posts)
        except Exception as error:
            print(error_handler(error))
