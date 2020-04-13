#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
import unittest

from hamcrest import assert_that
from hamcrest import has_entries
from hamcrest import starts_with

from six.moves import urllib_parse

from nti.oauthportal.authentication.url_utils import url_with_params

__docformat__ = "restructuredtext en"


class TestUrlWithParams(unittest.TestCase):

    def _query_params(self, url):
        url_parts = list(urllib_parse.urlparse(url))
        return dict(urllib_parse.parse_qsl(url_parts[4]))

    def _test_url_with_params(self,
                              input_url,
                              input_params,
                              expected_url_prefix,
                              expected_params):
        stripe_oauth_endpoint = url_with_params(
            input_url,
            input_params
        )

        assert_that(str(stripe_oauth_endpoint),
                    starts_with(expected_url_prefix))
        assert_that(self._query_params(stripe_oauth_endpoint),
                    has_entries(expected_params))

    def test_url_with_params_missing_params(self):
        self._test_url_with_params(
            "https://connect.stripe.com/oauth/authorize?scope=read_only&redirect_uri=uri_one",
            None,
            "https://connect.stripe.com/oauth/authorize",
            {
                "redirect_uri": "uri_one",
            }
        )

    def test_url_with_params_override(self):
        self._test_url_with_params(
            "https://connect.stripe.com/oauth/authorize?scope=read_only&redirect_uri=uri_one",
            {
                "response_type": "code",
                "scope": "read_write",
            },
            "https://connect.stripe.com/oauth/authorize",
            {
                "response_type": "code",
                "scope": "read_write",
                "redirect_uri": "uri_one"
            }
        )
