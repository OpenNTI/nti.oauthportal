#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib.parse as urllib_parse


def url_with_params(url, params):
    url_parts = list(urllib_parse.urlparse(url))
    query = dict(urllib_parse.parse_qsl(url_parts[4]))
    query.update(params)
    url_parts[4] = urllib_parse.urlencode(params)
    return urllib_parse.urlunparse(url_parts)

