import re

from bs4 import BeautifulSoup
from errorify import errorify

from fb_scraper.constants import FB_MBASIC_BASE_URL
from fb_scraper.utils import get_epoch_time


class PageExtractors:
    def __init__(self, _request) -> None:
        self.facebook = _request

    def post_id(self, content):
        try:
            value = None

            div = content.find('div', {'id': re.compile(r'^actions_\d+$')})

            if div:
                # match = re.search(r'&id=(\d+)', href)
                # value = match.group(1)
                value = div.get('id').split('_')[1]

            return value
        except Exception as error:
            print(errorify(error))
            return None

    def post_url(self, content):
        try:
            value = None

            href = content.get('href')

            if href:
                value = '&'.join(href.split('&')[0:2])

            return value
        except Exception as error:
            print(errorify(error))
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
            print(errorify(error))
            return None

    def reaction_count(self, content, story_id):
        try:
            value = None

            div = content.find('div', {'id': f'sentence_{story_id}'})

            if div:
                value = div.get_text()

                if re.search(r'\d+[kK]', value):
                    match = re.search(r'\d+', value)
                    value = str(int(match.group()) * 1000)

                if re.search(r'\d+[mM]', value):
                    match = re.search(r'\d+', value)
                    value = str(int(match.group()) * 100000)

            return value
        except Exception as error:
            print(errorify(error))
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
            print(errorify(error))
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
            print(errorify(error))
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
            print(errorify(error))
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
            print(errorify(error))
            return None

    def comments(self, content, story_id, post_id):
        try:
            values = []

            next_comments = True
            comment_div = content.find('div', {'id': f'ufi_{story_id}'})
            aggr_comment_div = content.find_all('div', {'id': f'ufi_{story_id}'})

            comment_div = aggr_comment_div.find_all('div', {'id': re.compile(r'^\d+$')}) if aggr_comment_div else []

            for div in comment_div:
                comment = {}
                comment['comment_id'] = self.comment_id(div)
                comment['comment_text'] = self.comment_text(div)
                comment['comment_time'] = self.comment_time(div)
                comment['commenter_id'] = self.commenter_id(div)
                comment['commenter_name'] = self.commenter_name(div)
                comment['commenter_url'] = self.commenter_url(div)
                comment['comment_reaction_count'] = self.comment_reaction_count(div)
                comment['replies'] = self.replies(div, post_id, comment['comment_id'])
                values.append(comment)

            while next_comments:
                next_url_div = comment_div.find('div', {'id': f'see_next_{story_id}'}) if comment_div is not None else None

                if not next_url_div:
                    break

                next_url_href = next_url_div.find('a').get('href') if next_url_div.find('a') else None

                if not next_url_href:
                    break
                else:
                    next_url_href = FB_MBASIC_BASE_URL + next_url_href

                print('Getting Comments')
                next_page_response = self.facebook.get(next_url_href)
                soup = BeautifulSoup(next_page_response, 'html.parser')
                next_comment_div = soup.find('div', {'id': f'ufi_{story_id}'})

                if not next_comment_div:
                    break

                comment_div = next_comment_div.find_all('div', {'id': re.compile(r'^\d+$')}) if aggr_comment_div else []

                for div in comment_div:
                    comment = {}
                    comment['comment_id'] = self.comment_id(div)
                    comment['comment_text'] = self.comment_text(div)
                    comment['comment_time'] = self.comment_time(div)
                    comment['commenter_id'] = self.commenter_id(div)
                    comment['commenter_name'] = self.commenter_name(div)
                    comment['commenter_url'] = self.commenter_url(div)
                    comment['comment_reaction_count'] = self.comment_reaction_count(div)
                    comment['replies'] = self.replies(div, post_id, comment['comment_id'])
                    values.append(comment)

            return values
        except Exception as error:
            print(errorify(error))
            return None

    def comment_id(self, content):
        try:
            value = None

            cid = content.get('id')

            if cid:
                value = cid

            return value
        except Exception as error:
            print(errorify(error))
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
            print(errorify(error))
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
            print(errorify(error))
            return None

    def commenter_name(self, content):
        try:
            value = None

            h3 = content.find('h3')

            if h3:
                value = h3.get_text()

            return value
        except Exception as error:
            print(errorify(error))
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
            print(errorify(error))
            return None

    def commenter_id(self, content):
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
            print(errorify(error))
            return None

    def comment_reaction_count(self, content):
        try:
            value = None

            a = content.find('a', {'aria-label': True})

            if a:
                value = a.get_text()

                if re.search(r'\d+[kK]', value):
                    match = re.search(r'\d+', value)
                    value = str(int(match.group()) * 1000)

                if re.search(r'\d+[mM]', value):
                    match = re.search(r'\d+', value)
                    value = str(int(match.group()) * 100000)

            return value
        except Exception as error:
            print(errorify(error))
            return None

    def replies(self, content, post_id, comment_id):
        try:
            values = []

            reply_url_div_id = f'comment_replies_more_1:{post_id}_{comment_id}'

            reply_url_div = content.find('div', {'id': reply_url_div_id})

            if reply_url_div:
                reply_url = reply_url_div.find('a').get('href') if reply_url_div.find('a') else None

                if reply_url:
                    print('Getting Replies')
                    scrape_type = {'scrape_type': 'reply'}
                    replies_response = self.facebook.get(FB_MBASIC_BASE_URL + reply_url, **scrape_type)

                    soup = BeautifulSoup(replies_response, 'html.parser')

                    reply_div = soup.find_all('div', {'id': re.compile(r'^\d+$')})

                    for div in reply_div:
                        reply = {}
                        if comment_id != div.get('id'):
                            reply['reply_id'] = self.comment_id(div)
                            reply['reply_text'] = self.comment_text(div)
                            reply['reply_time'] = self.comment_time(div)
                            reply['replier_id'] = self.commenter_id(div)
                            reply['replier_name'] = self.commenter_name(div)
                            reply['replier_url'] = self.commenter_url(div)
                            reply['reply_reaction_count'] = self.comment_reaction_count(div)
                            values.append(reply)

            return values
        except Exception as error:
            print(errorify(error))
            return None
