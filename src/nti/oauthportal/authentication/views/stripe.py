from pyramid.view import view_config

from nti.oauthportal.authentication.views import AbstractOAuthViews

OPENID_CONFIGURATION = None
DEFAULT_AUTH_URL = "https://connect.stripe.com/oauth/authorize"

logger = __import__('logging').getLogger(__name__)


class StripeOAuthViews(AbstractOAuthViews):

    session_key_prefix = 'stripe'

    def redirect_route(self):
        return self.request.route_url('stripe_oauth2')

    @view_config(route_name='stripe_oauth1')
    def authorization_request(self):
        return super(StripeOAuthViews, self).authorization_request()

    @view_config(route_name='stripe_oauth2')
    def authorization_return(self):
        return super(StripeOAuthViews, self).authorization_return()

    @property
    def authorization_endpoint(self):
        return DEFAULT_AUTH_URL
