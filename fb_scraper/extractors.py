from fb_scraper.constants import FB_MBASIC_BASE_URL


class Extractors:
    def profile_id(self, profile_content):
        profile_id = None

        link = profile_content.get('href')

        if link:
            if '?id' in link:
                profile_id = link.split('?id=')[1].split('&')[0]
            else:
                profile_id = link.split('?')[0].replace('/', '')

        return profile_id

    def profile_name(self, profile_content):
        profile_name = None

        text = profile_content.get_text(strip=True)

        if text:
            profile_name = text

        return profile_name

    def profile_url(self, profile_content):
        profile_url = None

        link = profile_content.get('href')

        if link:
            if '?id' in link:
                profile_url = FB_MBASIC_BASE_URL + '/' + link.split('?id=')[1].split('&')[0]
            else:
                profile_url = FB_MBASIC_BASE_URL + link.split('?')[0]

        return profile_url

    def post_url(self, post_url_content):
        post_url = None

        link = post_url_content.get('href')

        if link:
            post_url = link.split('?')[0]

        return post_url

    def post_id(self, post_url_content):
        post_id = None

        link = post_url_content.get('href')

        if link:
            post_id = link.split('?')[0].split('/')[6]

        return post_id

    def post_text(self, post_text_content):
        post_text = None

        post = post_text_content.get_text(strip=True)

        if post:
            post_text = post

        return post_text

    def comment_id(self, comment_content):
        comment_id = None

        comment = comment_content.get('id')

        if comment:
            comment_id = comment

        return comment_id

    def comment_text(self, comment_content):
        comment_text = None

        comment = comment_content.find('div', {'class': 'ec'})

        if comment:
            comment_text = comment.get_text(strip=True)

        return comment_text
