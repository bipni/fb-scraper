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
                print(f'{len(posts)} posts found in this page')

                extractors = Extractors()

                for i, post in enumerate(posts):
                    print(f'Post {i+1}')
                    group_post = {}

                    # get all link contents
                    link_contents = post.find_all('a')

                    for i, link_content in enumerate(link_contents):
                        # link content that contains 'Full Story' text has post url
                        if link_content.get_text(strip=True) == 'Full Story':
                            group_post['post_id'] = extractors.post_id(link_content)
                            group_post['post_url'] = extractors.post_url(link_content)

                    if 'post_url' in group_post and group_post['post_url'] is not None:
                        # get the specific post html response from facebook
                        post_response = self.get(group_post['post_url'])

                        soup = BeautifulSoup(post_response, 'html.parser')

                        group_post['post_text'] = extractors.post_text(soup)
                        group_post['reaction_count'] = extractors.reaction_count(soup, group_post['post_id'])
                        group_post['profile_id'] = extractors.profile_id(soup)
                        group_post['profile_name'] = extractors.profile_name(soup)
                        group_post['profile_url'] = extractors.profile_url(soup)
                        group_post['post_time'] = extractors.post_time(soup)
                        group_post['comments'] = extractors.comments(soup, group_post['post_id'])
                    else:
                        print('No post url found')

                    group_posts.append(group_post)
            else:
                print('No new posts found')

            print(group_posts)
        except Exception as error:
            print(error_handler(error))
