# -*- coding: utf-8 -*-
# Copyright 2017-2019, Schlumberger
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import os
import json
import tempfile
import time
from mock import patch

from sdlib.auth.providers.generic.oauth2 import OAuth2Service
from authlib.oauth2.rfc6749.wrappers import OAuth2Token

from test.utest import SdUtilTestCase


class TestAuth(SdUtilTestCase):
    def setUp(self):
        env_patcher = patch("os.getenv", lambda x: "!not-so-secret-client-id")
        self.mock_envs = env_patcher.start()
        self.addCleanup(env_patcher.stop)

    def mock_response(self, access_token, refresh_token, id_token, generate_stale=False):
        now = time.time()
        now += -3600 if generate_stale else +3600

        token = {
            'token_type': "Bearer",
            'scope': "x",
            'expires_in': 3600,
            'ext_expires_in': 3600,
            'access_token': access_token,
            'refresh_token': refresh_token,
            'id_token': id_token,
            'expires_at': now
        }
        return OAuth2Token.from_dict(token=token)

    def test_init_does_nothing_if_access_and_refresh_already_set(self):
        auth = OAuth2Service()
        auth._token = self.mock_response(
            access_token='a', refresh_token='r', id_token='i')
        auth._init()

        self.assertEqual(auth._token['access_token'], 'a')
        self.assertEqual(auth._token['refresh_token'], 'r')

    def test_init_reads_token_from_token_file(self):
        temp_files = []
        auth = OAuth2Service()
        token = self.mock_response(
            access_token='a', refresh_token='b', id_token='c')

        try:
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as token_fh:
                temp_files.append(token_fh.name)
                json.dump(token, token_fh)

            auth._token_file = token_fh.name
            auth._init()
        finally:
            # have to use finally remove with delete=False
            # as you cannot open temp file twice on windows
            list(map(os.remove, temp_files))

        assert auth._token == token

    def test_init_raises_exception_when_token_file_missing(self):
        auth = OAuth2Service()
        auth._token_file = 'dummyfile'
        with self.assertRaises(Exception):
            auth._init()

    @patch("sdlib.auth.providers.generic.oauth2.OAuth2Service._fetch_token")
    def test_refresh(self, mock_fetch):
        mock_fetch.return_value = self.mock_response(access_token='a', refresh_token='r', id_token='i',
                                                     generate_stale=True)
        auth = OAuth2Service()
        auth._init()

        self.assertTrue(auth._token.is_expired())

        with patch("authlib.integrations.requests_client.OAuth2Session.refresh_token") as mock_token:
            with patch("sdlib.auth.providers.generic.oauth2.OAuth2Service._update_token"):
                mock_token.return_value = self.mock_response(
                    access_token='a', refresh_token='r', id_token='j')
                auth.refresh()
                self.assertFalse(auth._token.is_expired())
                self.assertEqual(auth.get_id_token(), "j")

    def test_refresh_updates_token_file(self):
        temp_files = []
        auth = OAuth2Service(True)
        token = self.mock_response(
            access_token='a', refresh_token='b', id_token='c', generate_stale=True)

        try:
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as token_fh:
                temp_files.append(token_fh.name)
                json.dump(token, token_fh)

            with patch("authlib.integrations.requests_client.OAuth2Session.refresh_token") as mock_token:
                mock_token.return_value = self.mock_response(
                    access_token='a', refresh_token='x', id_token='c')

                auth._token_file = token_fh.name
                auth._init()

                assert auth._token == token
                assert auth._token.is_expired() is True

                auth.refresh()

                assert auth._token.is_expired() is False

            with open(token_fh.name, mode='r') as token_fh:
                new_token = json.load(token_fh)

            assert auth._token == new_token

        finally:
            # have to use finally remove with delete=False
            # as you cannot open temp file twice on windows
            list(map(os.remove, temp_files))

    @patch("sdlib.auth.providers.generic.oauth2.OAuth2Service._fetch_token")
    def test_get_id_token(self, mock_fetch):
        mock_fetch.return_value = self.mock_response(access_token='a', refresh_token='r', id_token='i',
                                                     generate_stale=True)

        auth = OAuth2Service()
        auth._init()

        self.assertTrue(auth._token.is_expired())
        self.assertEqual(auth._token['id_token'], 'i')

        with patch("authlib.integrations.requests_client.OAuth2Session.refresh_token") as mock_token:
            with patch("sdlib.auth.providers.generic.oauth2.OAuth2Service._update_token"):
                mock_token.return_value = self.mock_response(
                    access_token='a', refresh_token='r', id_token='j')

                self.assertEqual(auth.get_id_token(), "j")
                self.assertFalse(auth._token.is_expired())

    def test_get_id_token_when_set_w_init(self):
        id_token = "a"
        auth = OAuth2Service(idtoken=id_token)
        self.assertEqual(id_token, auth.get_id_token())

    @patch("sdlib.auth.providers.generic.oauth2.OAuth2Service._fetch_token")
    def test_fetch_access_token(self, mock_fetch):
        mock_fetch.return_value = self.mock_response(access_token='a', refresh_token='r', id_token='i',
                                                     generate_stale=True)

        auth = OAuth2Service()
        auth._init()

        self.assertTrue(auth._token.is_expired())
        self.assertEqual(auth._token['access_token'], 'a')

        with patch("authlib.integrations.requests_client.OAuth2Session.refresh_token") as mock_token:
            with patch("sdlib.auth.providers.generic.oauth2.OAuth2Service._update_token"):
                mock_token.return_value = self.mock_response(
                    access_token='b', refresh_token='r', id_token='j')
                self.assertEqual(auth.fetch_access_token(), "b")
                self.assertFalse(auth._token.is_expired())
                self.assertEqual(auth.fetch_access_token(), "b")

    @patch("sdlib.auth.providers.generic.oauth2.OAuth2Service._fetch_token")
    def test_fetch_refresh_token(self, mock_fetch):
        mock_fetch.return_value = self.mock_response(access_token='a', refresh_token='r', id_token='i',
                                                     generate_stale=True)

        auth = OAuth2Service()
        auth._init()

        self.assertTrue(auth._token.is_expired())
        self.assertEqual(auth._token['refresh_token'], 'r')

        with patch("authlib.integrations.requests_client.OAuth2Session.refresh_token") as mock_token:
            with patch("sdlib.auth.providers.generic.oauth2.OAuth2Service._update_token"):
                mock_token.return_value = self.mock_response(
                    access_token='a', refresh_token='s', id_token='j')
                self.assertEqual(auth.fetch_refresh_token(), "s")
                self.assertFalse(auth._token.is_expired())
                self.assertEqual(auth.fetch_refresh_token(), "s")
