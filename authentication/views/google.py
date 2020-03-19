from pyramid.view import view_config
from pyramid import httpexceptions as hexc
from pyramid.url import urlencode

import hashlib
import os

logger = __import__('logging').getLogger(__name__)


@view_config(route_name='home', renderer='../templates/mytemplate.pt')
def my_view(request):
    return {'project': 'authentication'}

@view_config(route_name='google_oauth1')
def initiate_logon(request):
    """
    Given a set of params suitable for the first step of the google oauth
    process, make the oauth redirect passing through params. We capture the
    provided state and redirect_uri in the session and replace them with our own
    state and redirect_uri. We restore the original in the second request of the flow.
    """

    # params = {
    #     'client_id': request.params['client_id'],
    #     'redirect_uri': request.route_url('google_oauth2'),
    #     'response_type': 'code',
    #     'scope': 'openid email profile'
    # }

    params = dict(request.params)

    # Capture the values we need to replace and stuff them in the session
    # See def:logon_return
    request.session['google.orig_redirect_uri'] = params.pop('redirect_uri')
    request.session['google.orig_state'] = params.pop('state')

    # Generate csrf state. stuff it in the session to compare against
    mystate = hashlib.sha256(os.urandom(1024)).hexdigest()
    request.session['google.state'] = mystate
    
    params['state'] = mystate
    params['redirect_uri'] = request.route_url('google_oauth2')

    qs = urlencode(params)

    location = 'https://accounts.google.com/o/oauth2/v2/auth?'+ qs

    # Send the user to the log in form
    return hexc.HTTPSeeOther(location)
    

@view_config(route_name='google_oauth2')
def logon_return(request):
    """
    Given an authorization code response, pass it on to our originally
    provided redirect_uri, replacing our swapped out state with the original
    state.
    """

    # Check our state
    state = request.params['state']
    mystate = request.session['google.state']

    if mystate != state:
        logger.warn('State mismatch')
        raise hexc.HTTPBadRequest()

    # Capture the incoming params, but replace the state with the orig_state
    # provided to us
    params = dict(request.params)
    params['state'] = request.session['google.orig_state']

    # Hmm. For our consumer to exchange the access code for a token we need to provide the
    # redirect_uri that was used to get the code. Can safely give that to our
    # caller? the client would have just made a request to that, so an end
    # user that knows what they are doing can find it. It's also sent as a query param
    # to google in the initial flow. I think this is ok???
    params['_redirect_uri'] = request.route_url('google_oauth2')

    location = request.session['google.orig_redirect_uri'] +'?' + urlencode(params)
    return hexc.HTTPSeeOther(location=location)
    
