from fb_scraper.exceptions import InvalidCookies
from fb_scraper.facebook_request import FacebookRequest
from fb_scraper.facebook_scraper import FacebookScraper
from fb_scraper.utils import parse_cookie_file


class Scraper:
    def __init__(self, cookies: list[str]) -> None:
        self.facebook_request = FacebookRequest(cookies)
        self.facebook_scraper = FacebookScraper(self.facebook_request)
        self.page_count = 1

    def get_group_posts_by_group_id(self, group_id: str, start_url: str = None):
        return self.facebook_scraper.get_group_posts_by_group_id(group_id, start_url)

    def get_page_posts_by_page_id(self, page_id: str, start_url: str = None):
        return self.facebook_scraper.get_page_posts_by_page_id(page_id, start_url)

    def get_profile(self, profile_id: str):
        return self.facebook_scraper.get_profile(profile_id)
