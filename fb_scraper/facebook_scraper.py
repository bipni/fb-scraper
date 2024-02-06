import random
import re
import time

from bs4 import BeautifulSoup

from fb_scraper.constants import FB_MBASIC_BASE_URL
from fb_scraper.error_handler import error_handler
from fb_scraper.exceptions import PrivateGroupError
from fb_scraper.group_extractors import GroupExtractors
from fb_scraper.page_extractors import PageExtractors
from fb_scraper.profile_extractors import ProfileExtractors


class FacebookScraper:
    def __init__(self, _request) -> None:
        self.facebook = _request

    def get_group_posts_by_group_id(self, group_id: str, start_url: str = None):
        try:
            group_posts = []
            url = FB_MBASIC_BASE_URL + '/groups' + f'/{group_id}'

            # if start_url, then scrape from start_url
            if start_url is not None:
                url = start_url

            # get the html response from facebook
            random_number = random.randint(2, 6)
            time.sleep(random_number)
            page_response = self.facebook.get(url)

            # parse html
            soup = BeautifulSoup(page_response, 'html.parser')

            # check if group is private
            header = soup.find('header')
            # form = soup.find('form', {'method': 'post', 'action': True})
            p = header.find('p') if header else []

            if p:
                for i in p:
                    if 'Private group' == i.get_text():
                        iinput = soup.find(lambda tag: tag.has_attr('value') and tag['value'] in ['Join Group', 'Cancel request'])
                        if iinput:
                            raise PrivateGroupError("User doesn't belong to this group")

            # article tag contains the post
            posts = soup.find_all('article')
            next_page_as = soup.find_all('a', string=lambda s: s and 'See more posts' in s)
            next_page_a = next_page_as[-1] if next_page_as else None
            next_page = FB_MBASIC_BASE_URL + next_page_a.get('href') if next_page_a else None

            if posts:
                print(f'{len(posts)} posts found in this page')

                extractors = GroupExtractors(self.facebook)

                for i, post in enumerate(posts):
                    print(f'Post {i+1} scraping')
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
                        post_response = self.facebook.get(group_post['post_url'])

                        soup = BeautifulSoup(post_response, 'html.parser')

                        # post related data
                        group_post['post_text'] = extractors.post_text(soup)
                        group_post['reaction_count'] = extractors.reaction_count(soup, group_post['post_id'])
                        group_post['profile_id'] = extractors.profile_id(soup)
                        group_post['profile_name'] = extractors.profile_name(soup)
                        group_post['profile_url'] = extractors.profile_url(soup)
                        group_post['post_time'] = extractors.post_time(soup)

                        # comment related data
                        group_post['comments'] = extractors.comments(soup, group_post['post_id'])
                    else:
                        print('No post url found')

                    group_posts.append(group_post)
            else:
                print('No new posts found')

            data = {
                'group_posts': group_posts,
                'next_url': next_page if next_page else None
            }

            return data
        except Exception as error:
            print(error_handler(error))

    def get_page_posts_by_page_id(self, page_id: str, start_url: str = None):
        try:
            page_posts = []
            url = None

            if page_id.isnumeric():
                # https://mbasic.facebook.com/profile.php?id=100077515030449&v=timeline
                url = FB_MBASIC_BASE_URL + '/profile.php?id=' + f'{page_id}&v=timeline'
            else:
                # https://mbasic.facebook.com/earkidotcom?v=timeline
                url = FB_MBASIC_BASE_URL + f'/{page_id}?v=timeline'

            # if start_url, then scrape from start_url
            if start_url is not None:
                url = start_url

            # get the html response from facebook
            random_number = random.randint(2, 6)
            time.sleep(random_number)
            page_response = self.facebook.get(url)

            # parse html
            soup = BeautifulSoup(page_response, 'html.parser')

            # article tag contains the post
            posts = soup.find_all('article')
            next_page_a = soup.find('a', string=lambda s: s and 'See more stories' in s)
            next_page = FB_MBASIC_BASE_URL + next_page_a.get('href') if next_page_a else None

            if posts:
                print(f'{len(posts)} posts found in this page')

                extractors = PageExtractors(self.facebook)

                for i, post in enumerate(posts):
                    print(f'Post {i+1} scraping')
                    page_post = {}

                    # get all link contents
                    link_contents = post.find_all('a')

                    for i, link_content in enumerate(link_contents):
                        # link content that contains 'Full Story' text has post url
                        if link_content.get_text(strip=True) == 'Full Story':
                            page_post['post_url'] = FB_MBASIC_BASE_URL + extractors.post_url(link_content)

                    if 'post_url' in page_post and page_post['post_url'] is not None:
                        # get the specific post html response from facebook
                        post_response = self.facebook.get(page_post['post_url'])

                        soup = BeautifulSoup(post_response, 'html.parser')

                        match = re.search(r'story_fbid=([a-zA-Z0-9]+)', page_post['post_url'])

                        if match:
                            story_id = match.group(1)

                        # post related data
                        page_post['post_id'] = extractors.post_id(soup)
                        page_post['post_text'] = extractors.post_text(soup)
                        page_post['reaction_count'] = extractors.reaction_count(soup, story_id)
                        page_post['post_time'] = extractors.post_time(soup)

                        # comment related data
                        page_post['comments'] = extractors.comments(soup, story_id, page_post['post_id'])
                    else:
                        print('No post url found')

                    page_posts.append(page_post)
            else:
                print('No new posts found')

            data = {
                'page_posts': page_posts,
                'next_url': next_page
            }

            return data
        except Exception as error:
            print(error_handler(error))

    def get_profile(self, profile_id: str):
        try:
            profile_info = {}
            url = None

            if profile_id.isnumeric():
                # https://mbasic.facebook.com/profile.php?id=100077515030449
                url = FB_MBASIC_BASE_URL + '/profile.php?id=' + f'{profile_id}'
            else:
                # https://mbasic.facebook.com/earkidotcom
                url = FB_MBASIC_BASE_URL + f'/{profile_id}'

            # get the html response from facebook
            profile_response = self.facebook.get(url)

            soup = BeautifulSoup(profile_response, 'html.parser')

            extractors = ProfileExtractors(self.facebook)

            profile_info['name'] = extractors.name(soup)

            if 'locked her profile' in str(profile_response) or 'locked his profile' in str(profile_response):
                profile_info['locked'] = True
            else:
                profile_info['locked'] = False

            a_tags = soup.find_all('a')

            if a_tags:
                for a in a_tags:
                    if 'About' in a.get_text():
                        href = FB_MBASIC_BASE_URL + a.get('href')
                        print(href)
                        about_response = self.facebook.get(href)
                        soup = BeautifulSoup(about_response, 'html.parser')

            profile_info['category'] = extractors.category(soup)
            profile_info['education'] = extractors.education(soup)
            profile_info['work'] = extractors.work(soup)
            profile_info['living'] = extractors.living(soup)
            profile_info['contact_info'] = extractors.contact_info(soup)
            profile_info['basic_info'] = extractors.basic_info(soup)
            profile_info['other_names'] = extractors.other_names(soup)
            profile_info['relationship'] = extractors.relationship(soup)
            profile_info['life_events'] = extractors.life_events(soup)
            profile_info['about'] = extractors.about(soup)
            profile_info['favorite_quote'] = extractors.favorite_quote(soup)

            return profile_info
        except Exception as error:
            print(error_handler(error))
