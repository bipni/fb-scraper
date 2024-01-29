import re

from bs4 import BeautifulSoup

from fb_scraper.constants import FB_MBASIC_BASE_URL
from fb_scraper.error_handler import error_handler
from fb_scraper.exceptions import PrivateGroupError
from fb_scraper.group_extractors import GroupExtractors
from fb_scraper.page_extractors import PageExtractors


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
            next_page_a = soup.find('a', string=lambda s: s and 'See more posts' in s)
            next_page = FB_MBASIC_BASE_URL + next_page_a.get('href')

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
            page_response = self.facebook.get(url)

            # parse html
            soup = BeautifulSoup(page_response, 'html.parser')

            # article tag contains the post
            posts = soup.find_all('article')
            next_page_a = soup.find('a', string=lambda s: s and 'See more stories' in s)
            next_page = FB_MBASIC_BASE_URL + next_page_a.get('href')

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

                        story_id = re.search(r'story_fbid=([a-zA-Z0-9]+)', page_post['post_url']).group(1)

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
