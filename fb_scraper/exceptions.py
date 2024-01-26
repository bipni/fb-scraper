class NotFound(Exception):
    '''Post, page or profile not found / doesn't exist / deleted'''


class TemporarilyBanned(Exception):
    '''User account rate limited'''


class AccountDisabled(Exception):
    '''User account disabled, with option to appeal'''


class InvalidCookies(Exception):
    '''Cookies file passed but missing cookies'''


class LoginRequired(Exception):
    '''Facebook requires a login to see this'''


class LoginError(Exception):
    '''Failed to log in'''


class UnexpectedResponse(Exception):
    '''Facebook served something weird'''


class PrivateGroupError(Exception):
    '''User doesn't belong to this group'''
