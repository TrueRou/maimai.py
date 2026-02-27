from http.cookiejar import CookieJar


class NullCookieJar(CookieJar):
    """A CookieJar that rejects all cookies."""

    def extract_cookies(self, response, request):
        """For extracting and saving cookies.  This implementation does nothing"""
        pass

    def set_cookie(self, cookie):
        """Normally for setting a cookie.  This implementation does nothing"""
        pass
