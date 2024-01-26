import re
import time
from datetime import datetime, timedelta

from dateutil import parser
from requests.cookies import RequestsCookieJar

from .exceptions import InvalidCookies


def parse_cookie_file(filename: str) -> RequestsCookieJar:
    jar = RequestsCookieJar()

    with open(filename, mode='rt', encoding='utf-8') as file:
        data = file.read()

    # only netscape format
    for i, line in enumerate(data.splitlines()):
        line = line.strip()

        if line == '' or line.startswith('#'):
            continue

        try:
            domain, _, path, secure, expires, name, value = line.split('\t')
        except Exception as error:
            raise InvalidCookies(f"Can't parse line {i + 1}: '{line}'") from error

        secure = secure.lower() == 'true'
        expires = None if expires == '0' else int(expires)

        jar.set(name, value, domain=domain, path=path, secure=secure, expires=expires)

    return jar


def get_epoch_time(date_string: str):
    try:
        epoch_time = None

        if 'hr' in date_string:
            match = re.search(r'\d+', date_string)
            hour = int(match.group())
            epoch_time = int(time.time()) - (hour * 60 * 60)
        elif 'min' in date_string:
            match = re.search(r'\d+', date_string)
            minute = int(match.group())
            epoch_time = int(time.time()) - (minute * 60)
        elif 'Yesterday' in date_string:
            today = datetime.now()
            yesterday = today - timedelta(days=1)
            formatted_yesterday = yesterday.strftime("%Y-%m-%d")
            date_string = date_string.replace('Yesterday', formatted_yesterday)
            epoch_time = int(parser.parse(date_string).timestamp())
        elif 'Today' in date_string:
            today = datetime.now()
            formatted_today = today.strftime("%Y-%m-%d")
            date_string = date_string.replace('Yesterday', formatted_today)
            epoch_time = int(parser.parse(date_string).timestamp())
        elif 'at' in date_string:
            epoch_time = int(parser.parse(date_string).timestamp())
        else:
            epoch_time = int(time.time())

        return epoch_time
    except Exception:
        print(f'Error: {date_string}')
        return None
