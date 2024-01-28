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
            value = None

            href = content.get('href')

            if href:
                value = href.split('?')[0].split('/')[6]

            return value
        except Exception as error:
            print(error_handler(error))
            return None

    def post_url(self, content):
        try:
            value = None

            href = content.get('href')

            if href:
                value = href.split('?')[0]

            return value
        except Exception as error:
            print(error_handler(error))
            return None

    def post_text(self, content):
        try:
            value = None

            div1 = content.find('div', {'data-ft': True})

            if div1:
                div2 = div1.find('div', {'data-ft': True})

                if div2:
                    value = div2.get_text()
                else:
                    value = div1.get_text()

            return value
        except Exception as error:
            print(error_handler(error))
            return None

    def reaction_count(self, content, post_id):
        try:
            value = None

            div = content.find('div', {'id': f'sentence_{post_id}'})

            if div:
                value = div.get_text()

                if 'k' in value:
                    match = re.search(r'\d+', value)
                    value = str(int(match.group()) * 1000)

                if 'm' in value:
                    match = re.search(r'\d+', value)
                    value = str(int(match.group()) * 100000)

            return value
        except Exception as error:
            print(error_handler(error))
            return None

    def profile_id(self, content):
        try:
            value = None

            h3 = content.find('h3')

            if h3:
                a = h3.find('a')

                if a:
                    href = a.get('href')

                    if href:
                        if '?id' in href:
                            value = href.split('?id=')[1].split('&')[0]
                        else:
                            value = href.split('?')[0].replace('/', '')

            return value
        except Exception as error:
            print(error_handler(error))
            return None

    def profile_name(self, content):
        try:
            value = None

            h3 = content.find('h3')

            if h3:
                a = h3.find('a')

                if a:
                    value = a.get_text(strip=True)

            return value
        except Exception as error:
            print(error_handler(error))
            return None

    def profile_url(self, content):
        try:
            value = None

            h3 = content.find('h3')

            if h3:
                a = h3.find('a')

                if a:
                    href = a.get('href')

                    if href:
                        if '?id' in href:
                            value = FB_MBASIC_BASE_URL + '/' + href.split('?id=')[1].split('&')[0]
                        else:
                            value = FB_MBASIC_BASE_URL + href.split('?')[0]

            return value
        except Exception as error:
            print(error_handler(error))
            return None

    def post_time(self, content):
        try:
            value = None

            footer = content.find('footer')

            if footer:
                abbr = footer.find('abbr')

                if abbr:
                    date_string = abbr.get_text()

                    value = get_epoch_time(date_string)

            return value
        except Exception as error:
            print(error_handler(error))
            return None

    def comments(self, content, post_id):
        try:
            values = []

            next_comments = True
            comment_div = content.find('div', {'id': f'ufi_{post_id}'})
            aggr_comment_div = content.find('div', {'id': f'ufi_{post_id}'})

            while next_comments:
                next_url_div = comment_div.find('div', {'id': f'see_next_{post_id}'})

                if not next_url_div:
                    break

                next_url_href = next_url_div.find('a').get('href') if next_url_div.find('a') else None

                if not next_url_href:
                    break

                next_page_response = self.facebook.get(next_url_href)
                soup = BeautifulSoup(next_page_response, 'html.parser')
                next_comment_div = soup.find('div', {'id': f'ufi_{post_id}'})

                if not next_comment_div:
                    break

                aggr_comment_div.append(next_comment_div)
                comment_div = next_comment_div

            comment_div = aggr_comment_div.find_all('div', {'id': re.compile(r'^\d+$')})

            for div in comment_div:
                comment = {}
                comment['comment_id'] = self.comment_id(div)
                comment['comment_text'] = self.comment_text(div)
                comment['comment_time'] = self.comment_time(div)
                comment['commenter_name'] = self.commenter_name(div)
                comment['commenter_url'] = self.commenter_url(div)
                comment['comment_reaction_count'] = self.comment_reaction_count(div)
                comment['replies'] = self.replies(div, post_id, comment['comment_id'])
                comment['replies_count'] = len(comment['replies'])
                values.append(comment)

            return values
        except Exception as error:
            print(error_handler(error))
            return None

    def comment_id(self, content):
        try:
            value = None

            cid = content.get('id')

            if cid:
                value = cid

            return value
        except Exception as error:
            print(error_handler(error))
            return None

    def comment_text(self, content):
        try:
            value = None

            div1 = content.find('div')
            div2 = div1.find('div')

            if div2:
                value = div2.get_text(strip=True)

            return value
        except Exception as error:
            print(error_handler(error))
            return None

    def comment_time(self, content):
        try:
            value = None

            abbr = content.find('abbr')

            if abbr:
                date_string = abbr.get_text()

                value = get_epoch_time(date_string)

            return value
        except Exception as error:
            print(error_handler(error))
            return None

    def commenter_name(self, content):
        try:
            value = None

            h3 = content.find('h3')

            if h3:
                value = h3.get_text()

            return value
        except Exception as error:
            print(error_handler(error))
            return None

    def commenter_url(self, content):
        try:
            value = None

            h3 = content.find('h3')

            if h3:
                a = h3.find('a')

                if a:
                    href = a.get('href')

                    if href:
                        if '?id' in href:
                            value = FB_MBASIC_BASE_URL + '/' + href.split('?id=')[1].split('&')[0]
                        else:
                            value = FB_MBASIC_BASE_URL + href.split('?')[0]

            return value
        except Exception as error:
            print(error_handler(error))
            return None

    def comment_reaction_count(self, content):
        try:
            value = None

            a = content.find('a', {'aria-label': True})

            if a:
                value = a.get_text()

                if 'k' in value:
                    match = re.search(r'\d+', value)
                    value = str(int(match.group()) * 1000)

                if 'm' in value:
                    match = re.search(r'\d+', value)
                    value = str(int(match.group()) * 100000)

            return value
        except Exception as error:
            print(error_handler(error))
            return None

    def replies(self, content, post_id, comment_id):
        try:
            values = []

            reply_url_div_id = f'comment_replies_more_1:{post_id}_{comment_id}'

            reply_url_div = content.find('div', {'id': reply_url_div_id})

            if reply_url_div:
                reply_url = reply_url_div.find('a').get('href') if reply_url_div.find('a') else None

                if reply_url:
                    replies_response = self.facebook.get(FB_MBASIC_BASE_URL + reply_url)

                    soup = BeautifulSoup(replies_response, 'html.parser')

                    reply_div = soup.find_all('div', {'id': re.compile(r'^\d+$')})

                    for div in reply_div:
                        reply = {}
                        if comment_id != div.get('id'):
                            reply['reply_id'] = self.comment_id(div)
                            reply['reply_text'] = self.comment_text(div)
                            reply['reply_time'] = self.comment_time(div)
                            reply['replier_name'] = self.commenter_name(div)
                            reply['replier_url'] = self.commenter_url(div)
                            reply['reply_reaction_count'] = self.comment_reaction_count(div)
                            values.append(reply)

            return values
        except Exception as error:
            print(error_handler(error))
            return None
