from bs4 import BeautifulSoup

from fb_scraper.constants import FB_MBASIC_BASE_URL
from fb_scraper.error_handler import error_handler
from fb_scraper.exceptions import PrivateGroupError
from fb_scraper.extractors import Extractors


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

                extractors = Extractors(self.facebook)

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
                        group_post['comment_count'] = len(group_post['comments'])
                    else:
                        print('No post url found')

                    group_posts.append(group_post)
            else:
                print('No new posts found')

            data = {
                'group_posts': group_posts,
                'next_url': next_page
            }
            print(data)
        except Exception as error:
            print(error_handler(error))
