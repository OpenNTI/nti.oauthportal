import multiprocessing

# Let true and false be synonyms for ease of
# the templaters
true = True
false = False

proxy_protocol = True
# Listen on all addresses to this port, and locally on this file
bind = [":6543"]
# Calculate worker number automatically if not
# specified
workers = "1" or multiprocessing.cpu_count() * 2 + 1
worker_class = "gevent"
accesslog = "-"
timeout = 1800
preload_app = False

forwarded_allow_ips = "" or "*"

# The maximum number of requests a worker will process before
# restarting. Any value greater than zero will limit the number of
# requests a work will process before automatically restarting. This
# is a simple method to help limit the damage of memory leaks. If this
# is set to zero (the default) then the automatic worker restarts are
# disabled.
max_requests = 0

# The maximum number of simultaneous clients. This setting only
# affects the Eventlet and Gevent worker types.
worker_connections = 250
