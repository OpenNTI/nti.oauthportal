import unittest
import urllib.parse as urllib_parse

import fudge
from hamcrest import assert_that
from hamcrest import calling
from hamcrest import contains_string
from hamcrest import has_entries
from hamcrest import is_
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

    captured_message = None

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

    def _test_oauth(self, auth_service_name, base_auth_url):
        orig_state = self._encode({
            "state": "abc123",
            "redirect_uri": "https://mydomain.com/path/?existing_param=112233"
        })
        oauth1_url = f"/{auth_service_name}/oauth1?state=%s" % (orig_state,)
        res = self.testapp.get(oauth1_url, status=303)
        assert_that(res.headers['location'], starts_with(base_auth_url))

        loc_params = self._query_params(res.headers['location'])
        assert_that(loc_params, has_entries({
            "state": not_("abc123"),
            "redirect_uri": f"http://localhost/{auth_service_name}/oauth2",
        }))

        oauth2_url = f'/{auth_service_name}/oauth2?state=%s&code=1234' % (loc_params['state'],)
        res = self.testapp.get(oauth2_url, status=303)
        assert_that(res.headers['location'], starts_with("https://mydomain.com/path/"))

        loc_params = self._query_params(res.headers['location'])
        assert_that(loc_params, has_entries({
            "state": orig_state,
            "existing_param": "112233",
            "code": "1234"
        }))

    def _encode(self, params):
        signer = ContentSigner(self.secret, self.salt)
        return signer.encode(params)

    @fudge.patch("nti.oauthportal.authentication.views.google.get_openid_configuration")
    def test_google_oauth1_success(self, get_openid_config):
        get_openid_config.is_callable().returns({})

        self._test_oauth("google", "https://accounts.google.com/o/oauth2/v2/auth")

    def test_stripe_oauth1_success(self):
        self._test_oauth("stripe", "https://connect.stripe.com/oauth/authorize")

    @fudge.patch('nti.oauthportal.authentication.views.logger')
    def test_stripe_oauth1_no_state(self, logger):
        def capture_log_output(msg, *args, **kwargs):
            self.captured_message = msg
        logger.provides('error').calls(capture_log_output)

        res = self.testapp.get("/stripe/oauth1", status=200)
        assert_that(str(res.body), contains_string("An error occurred during authorization"))
        assert_that(self.captured_message, starts_with("Missing state for authorization request."))

    @fudge.patch('nti.oauthportal.authentication.views.logger')
    def test_stripe_oauth1_no_redirect_uri(self, logger):
        def capture_log_output(msg, *args, **kwargs):
            self.captured_message = msg
        logger.provides('error').calls(capture_log_output)

        orig_state = self._encode({
            "state": "abc123",
        })
        oauth1_url = f"/stripe/oauth1?state={orig_state}"

        res = self.testapp.get(oauth1_url, status=200)
        assert_that(str(res.body), contains_string("An error occurred during authorization"))
        assert_that(self.captured_message, starts_with("Missing redirect_uri"))

    @fudge.patch('nti.oauthportal.authentication.views.logger')
    def test_stripe_oauth2_no_redirect_uri(self, logger):
        captured_args = []

        def capture_log_output(msg, *args, **kwargs):
            self.captured_message = msg
            captured_args.extend(args)
        logger.provides('error').calls(capture_log_output)

        orig_state = self._encode({
            "state": "abc123",
            "redirect_uri": "https://mydomain.com/path/?existing_param=112233"
        })
        oauth1_url = f"/stripe/oauth1?state=%s" % (orig_state,)
        self.testapp.get(oauth1_url, status=303)

        oauth2_url = f"/stripe/oauth2?state=xyz321"
        res = self.testapp.get(oauth2_url, status=303)
        assert_that(res.headers['location'], starts_with("https://mydomain.com/path"))
        loc_params = self._query_params(res.headers['location'])

        assert_that(loc_params, has_entries({
            "error": "Server Error",
            "error_description": starts_with("An error occurred during authorization")
        }))
        assert_that(self.captured_message, starts_with("State returned (%s) doesn't match"))
        assert_that(captured_args[0], is_("xyz321"))
