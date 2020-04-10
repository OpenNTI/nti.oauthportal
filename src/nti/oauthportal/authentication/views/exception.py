from pyramid.view import exception_view_config


@exception_view_config(Exception, renderer='nti.oauthportal.authentication:templates/authorization_error.pt')
def error_view(request):
    return {'error': str(request.exception)}
