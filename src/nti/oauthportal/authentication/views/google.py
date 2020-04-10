import requests

from pyramid.view import view_config

from nti.oauthportal.authentication.views import AbstractOAuthViews

OPENID_CONFIGURATION = None
DEFAULT_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
DISCOVERY_DOC_URL = 'https://accounts.google.com/.well-known/openid-configuration'

logger = __import__('logging').getLogger(__name__)


def get_openid_configuration():
    global OPENID_CONFIGURATION
    if not OPENID_CONFIGURATION:
        s = requests.get(DISCOVERY_DOC_URL)
        OPENID_CONFIGURATION = s.json() if s.status_code == 200 else {}
    return OPENID_CONFIGURATION


class GoogleOAuthViews(AbstractOAuthViews):

    session_key_prefix = 'google'

    def redirect_route(self):
        return self.request.route_url('google_oauth2')

    @view_config(route_name='google_oauth1')
    def authorization_request(self):
        return super(GoogleOAuthViews, self).authorization_request()

    @view_config(route_name='google_oauth2')
    def authorization_return(self):
        return super(GoogleOAuthViews, self).authorization_return()

    @property
    def authorization_endpoint(self):
        config = get_openid_configuration()
        return config.get("authorization_endpoint", DEFAULT_AUTH_URL)
