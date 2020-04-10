import unittest

from hamcrest import assert_that
from hamcrest import calling
from hamcrest import raises
from pyramid import testing

from nti.oauthportal.authentication.views import AuthorizationError


class ViewTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_google_no_state(self):
        from .views.google import GoogleOAuthViews
        request = testing.DummyRequest()
        info = GoogleOAuthViews(request)
        assert_that(calling(info.authorization_request), raises(AuthorizationError))


class FunctionalTests(unittest.TestCase):
    def setUp(self):
        from nti.oauthportal.authentication import main
        app = main({}, **{
            "signer.secret": "itsaseekreet",
            "signer.salt": "itsasaltee"
        })
        from webtest import TestApp
        self.testapp = TestApp(app)

    def test_root(self):
        res = self.testapp.get('/google/oauth1', status=200)
        self.assertTrue(b'Authorization Error' in res.body)
