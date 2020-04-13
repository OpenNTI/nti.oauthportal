import unittest
import urllib.parse as urllib_parse

import fudge
from hamcrest import assert_that
from hamcrest import calling
from hamcrest import has_entries
from hamcrest import not_
from hamcrest import raises
from hamcrest import starts_with
from pyramid import testing

from nti.common.model import ContentSigner
from nti.oauthportal.authentication.views import AuthorizationError


class ViewTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_google_no_state(self):
        from ..views.google import GoogleOAuthViews
        request = testing.DummyRequest()
        info = GoogleOAuthViews(request)
        assert_that(calling(info.authorization_request), raises(AuthorizationError))


class FunctionalTests(unittest.TestCase):
    secret = "itsaseekreet"
    salt = "itsasaltee"

    def setUp(self):
        from nti.oauthportal.authentication import main
        app = main({}, **{
            "signer.secret": self.secret,
            "signer.salt": self.salt
        })
        from webtest import TestApp
        self.testapp = TestApp(app)

    def _query_params(self, url):
        url_parts = list(urllib_parse.urlparse(url))
        return dict(urllib_parse.parse_qsl(url_parts[4]))

    def test_no_state(self):
        res = self.testapp.get('/google/oauth1', status=200)
        self.assertTrue(b'Authorization Error' in res.body)

    @fudge.patch("nti.oauthportal.authentication.views.google.get_openid_configuration")
    def test_success(self, get_openid_config):
        get_openid_config.is_callable().returns({})

        signer = ContentSigner(self.secret, self.salt)
        orig_state = signer.encode({
            "state": "abc123",
            "redirect_uri": "https://mydomain.com/path/?existing_param=112233"
        })
        res = self.testapp.get('/google/oauth1?state=%s' % (orig_state,), status=303)
        assert_that(res.headers['location'], starts_with("https://accounts.google.com/o/oauth2/v2/auth"))

        loc_params = self._query_params(res.headers['location'])
        assert_that(loc_params, has_entries({
            "state": not_("abc123"),
            "redirect_uri": "http://localhost/google/oauth2",
        }))

        res = self.testapp.get('/google/oauth2?state=%s&code=1234' % (loc_params['state'],), status=303)
        assert_that(res.headers['location'], starts_with("https://mydomain.com/path/"))

        loc_params = self._query_params(res.headers['location'])
        assert_that(loc_params, has_entries({
            "state": orig_state,
            "existing_param": "112233",
            "code": "1234"
        }))
