from fb_scraper.error_handler import error_handler


class ProfileExtractors:
    def __init__(self, _request) -> None:
        self.facebook = _request

    def name(self, content):
        try:
            value = None

            strong_tags = content.find_all('strong')

            if strong_tags:
                for strong in strong_tags:
                    text = strong.get_text()

                    if 'Messages' not in text or 'Friends' not in text or 'Notifications' not in text:
                        value = text

            return value
        except Exception as error:
            print(error_handler(error))
            return None

    def category(self, content):
        try:
            value = None

            div = content.find('div', {'id': 'category'})

            if div:
                text = div.get_text()

                value = text.replace('Category', '')

            return value
        except Exception as error:
            print(error_handler(error))
            return None

    def education(self, content):
        try:
            value = None

            div1 = content.find('div', {'id': 'education'})
            div2 = div1.find('div') if div1 is not None else None
            header = div2.find('header') if div2 is not None else None
            div3 = header.find_next_sibling('div') if header is not None else None
            divs = div3.find_all('div', recursive=False) if div3 is not None else None

            if divs and len(divs):
                section = []
                for div in divs:
                    section.append(div.get_text(separator=','))

                value = section

            return value
        except Exception as error:
            print(error_handler(error))
            return None

    def work(self, content):
        try:
            value = None

            div1 = content.find('div', {'id': 'work'})
            div2 = div1.find('div') if div1 is not None else None
            header = div2.find('header') if div2 is not None else None
            div3 = header.find_next_sibling('div') if header is not None else None
            divs = div3.find_all('div', recursive=False) if div3 is not None else None

            if divs and len(divs):
                section = []
                for div in divs:
                    section.append(div.get_text(separator=','))

                value = section

            return value
        except Exception as error:
            print(error_handler(error))
            return None

    def living(self, content):
        try:
            value = None

            div1 = content.find('div', {'id': 'living'})
            div2 = div1.find('div') if div1 is not None else None
            header = div2.find('header') if div2 is not None else None
            div3 = header.find_next_sibling('div') if header is not None else None
            divs = div3.find_all('div', recursive=False) if div3 is not None else None

            if divs and len(divs):
                section = {}
                for div in divs:
                    tds = div.find_all('td', {'valign': True})

                    if tds:
                        key = tds[0].get_text().lower()
                        text = tds[1].get_text()
                        section[key] = text

                value = section

            return value
        except Exception as error:
            print(error_handler(error))
            return None

    def contact_info(self, content):
        try:
            value = None

            div1 = content.find('div', {'id': 'contact-info'})
            div2 = div1.find('div') if div1 is not None else None
            header = div2.find('header') if div2 is not None else None
            div3 = header.find_next_sibling('div') if header is not None else None
            divs = div3.find_all('div', recursive=False) if div3 is not None else None

            if divs and len(divs):
                section = {}
                for div in divs:
                    tds = div.find_all('td', {'valign': True})

                    if tds:
                        key = tds[0].get_text().lower()
                        text = tds[1].get_text()
                        section[key] = text

                value = section

            return value
        except Exception as error:
            print(error_handler(error))
            return None

    def basic_info(self, content):
        try:
            value = None

            div1 = content.find('div', {'id': 'basic-info'})
            div2 = div1.find('div') if div1 is not None else None
            header = div2.find('header') if div2 is not None else None
            div3 = header.find_next_sibling('div') if header is not None else None
            divs = div3.find_all('div', recursive=False) if div3 is not None else None

            if divs and len(divs):
                section = {}
                for div in divs:
                    tds = div.find_all('td', {'valign': True})

                    if tds:
                        key = tds[0].get_text().lower()
                        text = tds[1].get_text()
                        section[key] = text

                value = section
            return value
        except Exception as error:
            print(error_handler(error))
            return None

    def other_names(self, content):
        try:
            value = None

            div1 = content.find('div', {'id': 'nicknames'})
            div2 = div1.find('div') if div1 is not None else None
            header = div2.find('header') if div2 is not None else None
            div3 = header.find_next_sibling('div') if header is not None else None
            divs = div3.find_all('div', recursive=False) if div3 is not None else None

            if divs and len(divs):
                section = {}
                for div in divs:
                    tds = div.find_all('td', {'valign': True})

                    if tds:
                        key = tds[0].get_text().lower()

                        if key not in section:
                            section[key] = []

                        text = tds[1].get_text()
                        section[key].append(text)

                value = section
            return value
        except Exception as error:
            print(error_handler(error))
            return None

    def relationship(self, content):
        try:
            value = None

            div = content.find('div', {'id': 'relationship'})

            if div:
                text = div.get_text(separator=',')

                value = text.replace('Relationship,', '')

            return value
        except Exception as error:
            print(error_handler(error))
            return None

    def life_events(self, content):
        try:
            value = None

            div1 = content.find('div', {'id': 'year-overviews'})
            div2 = div1.find('div') if div1 is not None else None
            header = div2.find('header') if div2 is not None else None
            div3 = header.find_next_sibling('div') if header is not None else None
            top_level_divs = div3.find_all('div', recursive=False) if div3 is not None else None
            divs = [div for div in top_level_divs if div.get_text(strip=True)] if top_level_divs is not None else None

            if divs and len(divs):
                section = []
                for div in divs:
                    section.append(div.get_text(separator=','))

                value = section

            return value
        except Exception as error:
            print(error_handler(error))
            return None

    def about(self, content):
        try:
            value = None

            div = content.find('div', {'id': 'bio'})

            if div:
                text = div.get_text(separator=',')

                value = ','.join(text.split(',')[1:])

            return value
        except Exception as error:
            print(error_handler(error))
            return None

    def favorite_quote(self, content):
        try:
            value = None

            div = content.find('div', {'id': 'quote'})

            if div:
                text = div.get_text(separator=',')

                value = text.replace('Favorite quotes,', '')

            return value
        except Exception as error:
            print(error_handler(error))
            return None
