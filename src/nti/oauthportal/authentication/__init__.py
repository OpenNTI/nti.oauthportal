import os

from pyramid.config import Configurator
from pyramid.session import JSONSerializer

from pyramid.session import SignedCookieSessionFactory


def maybe_set(settings, name, envvar):
    if envvar in os.environ:
        value = os.environ[envvar]
        settings[name] = value


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """

    maybe_set(settings, 'signer.secret', 'SIGNER_SECRET')
    maybe_set(settings, 'signer.salt', 'SIGNER_SALT')
    with Configurator(settings=settings) as config:
        my_session_factory = SignedCookieSessionFactory(settings['signer.secret'],
                                                        serializer=JSONSerializer())
        config.set_session_factory(my_session_factory)

        config.include('pyramid_chameleon')
        config.include('.routes')
        config.include('.signer')
        config.scan(ignore=".tests")
    return config.make_wsgi_app()
