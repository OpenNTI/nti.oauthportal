def includeme(config):
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('google_oauth1', '/google/oauth1')
    config.add_route('google_oauth2', '/google/oauth2')
    config.add_route('stripe_oauth1', '/stripe/oauth1')
    config.add_route('stripe_oauth2', '/stripe/oauth2')
