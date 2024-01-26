import re

from bs4 import BeautifulSoup

from fb_scraper.constants import FB_MBASIC_BASE_URL
from fb_scraper.error_handler import error_handler
from fb_scraper.utils import get_epoch_time


class Extractors:
    def __init__(self, _request) -> None:
        self.facebook = _request

    def post_id(self, content):
        try:
            post_id = None

            link = content.get('href')

            if link:
                post_id = link.split('?')[0].split('/')[6]

            return post_id
        except Exception as error:
            print(error_handler(error))
            return None

    def post_url(self, content):
        try:
            post_url = None

            link = content.get('href')

            if link:
                post_url = link.split('?')[0]

            return post_url
        except Exception as error:
            print(error_handler(error))
            return None

    def post_text(self, content):
        try:
            post_text = None

            post = content.find('div', {'data-ft': True}).find('div', {'data-ft': True})

            if post:
                post_text = post.get_text()

            return post_text
        except Exception as error:
            print(error_handler(error))
            return None

    def reaction_count(self, content, post_id):
        try:
            reaction_count = None

            reaction = content.find('div', {'id': f'sentence_{post_id}'})

            if reaction:
                reaction_count = reaction.get_text()

            return reaction_count
        except Exception as error:
            print(error_handler(error))
            return None

    def profile_id(self, content):
        try:
            profile_id = None

            # first h3 tag contains the user
            profile_section = content.find('h3')

            if profile_section:
                a_tag = profile_section.find('a')

                if a_tag:
                    link = a_tag.get('href')

                    if link:
                        if '?id' in link:
                            profile_id = link.split('?id=')[1].split('&')[0]
                        else:
                            profile_id = link.split('?')[0].replace('/', '')

            return profile_id
        except Exception as error:
            print(error_handler(error))
            return None

    def profile_name(self, content):
        try:
            profile_name = None

            # first h3 tag contains the user
            profile_section = content.find('h3')

            if profile_section:
                a_tag = profile_section.find('a')

                if a_tag:
                    profile_name = a_tag.get_text(strip=True)

            return profile_name
        except Exception as error:
            print(error_handler(error))
            return None

    def profile_url(self, content):
        try:
            profile_url = None

            # first h3 tag contains the user
            profile_section = content.find('h3')

            if profile_section:
                a_tag = profile_section.find('a')

                if a_tag:
                    link = a_tag.get('href')

                    if link:
                        if '?id' in link:
                            profile_url = FB_MBASIC_BASE_URL + '/' + link.split('?id=')[1].split('&')[0]
                        else:
                            profile_url = FB_MBASIC_BASE_URL + link.split('?')[0]

            return profile_url
        except Exception as error:
            print(error_handler(error))
            return None

    def post_time(self, content):
        try:
            post_time = None

            # footer tag contains the time
            footer = content.find('footer')

            if footer:
                abbr = footer.find('abbr')

                if abbr:
                    date_string = abbr.get_text()

                    post_time = get_epoch_time(date_string)

            return post_time
        except Exception as error:
            print(error_handler(error))
            return None

    def comments(self, content, post_id):
        try:
            comments = []

            next_comments = True
            comment_section = content.find('div', {'id': f'ufi_{post_id}'})
            aggr_comment_section = content.find('div', {'id': f'ufi_{post_id}'})

            while (next_comments):
                next_url_div = comment_section.find('div', {'id': f'see_next_{post_id}'})

                if not next_url_div:
                    break

                next_url = next_url_div.find('a').get('href') if next_url_div.find('a') else None

                if not next_url:
                    break

                next_response = self.facebook.get(next_url)
                soup = BeautifulSoup(next_response, 'html.parser')
                next_comment_section = soup.find('div', {'id': f'ufi_{post_id}'})

                if not next_comment_section:
                    break

                aggr_comment_section.append(next_comment_section)
                comment_section = next_comment_section

            comment_div = aggr_comment_section.find_all('div', {'id': re.compile(r'^\d+$')})

            for div in comment_div:
                comment = {}
                comment['comment_id'] = self.comment_id(div)
                comment['comment_text'] = self.comment_text(div)
                comment['comment_time'] = self.comment_time(div)
                comment['commenter_name'] = self.commenter_name(div)
                comment['comment_reaction_count'] = self.comment_reaction_count(div)
                comments.append(comment)

            return comments
        except Exception as error:
            print(error_handler(error))
            return None

    def comment_id(self, content):
        try:
            comment_id = None

            comment = content.get('id')

            if comment:
                comment_id = comment

            return comment_id
        except Exception as error:
            print(error_handler(error))
            return None

    def comment_text(self, content):
        try:
            comment_text = None

            comment = content.find('div').find('div')

            if comment:
                comment_text = comment.get_text(strip=True)

            return comment_text
        except Exception as error:
            print(error_handler(error))
            return None

    def comment_time(self, content):
        try:
            comment_time = None

            abbr = content.find('abbr')

            if abbr:
                date_string = abbr.get_text()

                comment_time = get_epoch_time(date_string)

            return comment_time
        except Exception as error:
            print(error_handler(error))
            return None

    def commenter_name(self, content):
        try:
            commenter_name = None

            comment = content.find('h3')

            if comment:
                commenter_name = comment.get_text()

            return commenter_name
        except Exception as error:
            print(error_handler(error))
            return None

    def comment_reaction_count(self, content):
        try:
            comment_reaction_count = None

            comment = content.find('a', {'aria-label': True})

            if comment:
                comment_reaction_count = comment.get_text()

            return comment_reaction_count
        except Exception as error:
            print(error_handler(error))
            return None
