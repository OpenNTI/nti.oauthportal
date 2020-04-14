import hashlib
import os
from uuid import uuid4

from pyramid import httpexceptions as hexc
from zope.cachedescriptors.property import Lazy

from nti.common.interfaces import IContentSigner
from nti.oauthportal.authentication.exceptions import AuthorizationError
from nti.oauthportal.authentication.url_utils import url_with_params

logger = __import__('logging').getLogger(__name__)


def redirect_with_params(loc, params):
    url = url_with_params(loc, params)
    return hexc.HTTPSeeOther(url)


class AbstractOAuthViews(object):

    def __init__(self, request):
        self.request = request

    @Lazy
    def _serializer(self):
        return self.request.registry.getUtility(IContentSigner)

    def _unpack_state(self, signed_state):
        signed_state = self._serializer.decode(signed_state)
        return signed_state.get("state"), signed_state.get("redirect_uri")

    def error_response(self, loc, error='Unknown', desc='An unknown error occurred'):
        return redirect_with_params(loc, {'error': error, 'error_description': desc})

    def authorization_error(self, msg):
        error_uid = str(uuid4())
        logger.error(msg, error_uid)
        raise AuthorizationError(
            "An error occurred during authorization: %s" % (error_uid,))

    def _do_authorization_request(self):
        """
        Given a set of params suitable for the first step of the oauth
        process, make the oauth redirect passing through params. We capture the
        provided state and redirect_uri in the session and replace them with our own
        state and redirect_uri. We restore the original in the second request of the flow.
        """

        params = dict(self.request.params)

        state = params.pop('state', None)
        if not state:
            self.authorization_error(
                "Missing state for authorization request. "
                "No way to obtain or validate redirect uri (%s). ")

        self.request.session[self.session_key('orig_state')] = state

        # The state sent to the portal is a dict containing both the
        # original random state and the redirect uri, signed to ensure
        # we accept only verified redirect_uris, we ignore any other
        # redirect uri passed, to avoid acting as an open
        # redirector (https://tools.ietf.org/html/rfc6819#section-4.2.4)
        _, redirect_uri = self._unpack_state(state)

        if not redirect_uri:
            self.authorization_error(
                "Missing redirect_uri specified in state for authorization "
                "request. Unable to redirect after authorization.")

        # Capture the values we need to replace and stuff them in the session
        # See def:logon_return
        self.request.session[self.session_key('orig_redirect_uri')] = redirect_uri

        # Generate csrf state. stuff it in the session to compare against
        mystate = hashlib.sha256(os.urandom(1024)).hexdigest()
        self.request.session[self.session_key('state')] = mystate

        params['state'] = mystate
        params['redirect_uri'] = self.redirect_route()

        # Send the user to the log in form
        return redirect_with_params(self.authorization_endpoint, params)

    def authorization_request(self):
        try:
            return self._do_authorization_request()
        except AuthorizationError:
            raise
        except Exception:
            error_uid = str(uuid4())
            msg = "An error occurred during authorization: %s" % (error_uid,)
            logger.exception(msg)
            raise AuthorizationError(msg)

    def redirect_route(self):
        raise NotImplementedError()

    @property
    def session_key_prefix(self):
        raise NotImplementedError()

    @property
    def authorization_endpoint(self):
        raise NotImplementedError()

    def session_key(self, key):
        return '%s.%s' % (self.session_key_prefix, key)

    @property
    def _response_location(self):
        return self.request.session[self.session_key('orig_redirect_uri')]

    def _do_authorization_return(self):
        """
        Given an authorization code response, pass it on to our originally
        provided redirect_uri, replacing our swapped out state with the original
        state.
        """

        # Check our state
        state = self.request.params['state']
        session_state = self.request.session[self.session_key('state')]

        if session_state != state:
            error_uid = str(uuid4())
            logger.error("State returned (%s) doesn't match state sent (%s)",
                         state,
                         session_state)
            return self.error_response(self._response_location,
                                       "Server Error",
                                       "An error occurred during authorization: %s" % (error_uid,))

        # Capture the incoming params, but replace the state with the orig_state
        # provided to us
        params = dict(self.request.params)
        params['state'] = self.request.session[self.session_key('orig_state')]

        # Some authorization servers bind authorization codes to the
        # redirect URI used during the authorization process and this needs
        # to be used during the token request.
        # See https://tools.ietf.org/html/rfc6819#section-5.2.4.5
        params['_redirect_uri'] = self.redirect_route()

        return redirect_with_params(self._response_location, params)

    def authorization_return(self):
        try:
            return self._do_authorization_return()
        except Exception:
            error_uid = str(uuid4())
            msg = "An error occurred during authorization: %s" % (error_uid,)
            logger.exception(msg)
            return self.error_response(self._response_location,
                                       "Server Error",
                                       "An error occurred during authorization: %s" % (error_uid,))
