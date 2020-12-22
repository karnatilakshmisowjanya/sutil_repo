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

from authlib.integrations.requests_client import OAuth2Session
from authlib.oauth2.rfc6749.wrappers import OAuth2Token
from authlib.integrations.flask_client import OAuth

from sdlib.auth.auth_service import AuthService, AuthFactory
from sdlib.shared.config import Config

from .login import login
from .logout import logout


@AuthFactory.register(provider="oauth2")
class OAuth2Service(AuthService):
    """
    A wrapper class for any OAuth2 provider based on Authlib
    https://docs.authlib.org/en/stable/index.html
    """

    __OAUTH2_REDIRECT_URI = 'http://localhost:4300/auth/callback'
    __OAUTH2_TOKEN_FILE = 'auth.token'

    __OAUTH2_CLIENT_ID = None
    __OAUTH2_CLIENT_SECRET = None

    def __init__(self, idtoken=None):
        self.__is_init = False
        self._id_token = idtoken

        assert os.getenv("OAUTH2_CLIENT_ID"), "\n- environment variable \"OAUTH2_CLIENT_ID\" not set"
        assert os.getenv("OAUTH2_CLIENT_SECRET"), "\n- environment variable\"OAUTH2_CLIENT_SECRET\" not set"

        OAuth2Service.__OAUTH2_CLIENT_ID = os.getenv("OAUTH2_CLIENT_ID")
        OAuth2Service.__OAUTH2_CLIENT_SECRET = os.getenv("OAUTH2_CLIENT_SECRET")

        OAuth2Service.__OAUTH2_PROVIDER = Config.OAUTH2.PROVIDER
        OAuth2Service.__OAUTH2_AUTHORIZE_URL = Config.OAUTH2.AUTHORIZE_URL
        OAuth2Service.__OAUTH2_AUTHORIZE_PARAMS = Config.OAUTH2.AUTHORIZE_PARAMS
        OAuth2Service.__OAUTH2_REFRESH_TOKEN_URL = Config.OAUTH2.REFRESH_TOKEN_URL
        OAuth2Service.__OAUTH2_REFRESH_TOKEN_PARAMS = Config.OAUTH2.REFRESH_TOKEN_PARAMS
        OAuth2Service.__OAUTH2_ACCESS_TOKEN_URL = Config.OAUTH2.ACCESS_TOKEN_URL
        OAuth2Service.__OAUTH2_ACCESS_TOKEN_PARAMS = Config.OAUTH2.ACCESS_TOKEN_PARAMS
        OAuth2Service.__OAUTH2_SCOPE = Config.OAUTH2.SCOPE
        OAuth2Service.__OAUTH2_OPEN_ID_URL = Config.OAUTH2.OPEN_ID_URL
        
        self._oauth_client = OAuth2Session(
            client_id=OAuth2Service.__OAUTH2_CLIENT_ID,
            client_secret=OAuth2Service.__OAUTH2_CLIENT_SECRET,
            scope=OAuth2Service.__OAUTH2_SCOPE,
            redirect_uri=OAuth2Service.__OAUTH2_REDIRECT_URI,
            token=None
        )
        self._token_dir = os.path.join(os.path.expanduser("~"), Config.HOME)
        self._token_file = os.path.join(self._token_dir, OAuth2Service.__OAUTH2_TOKEN_FILE)
        self._token = None

    def _init(self):
        self.__is_init = True
        if not self._token:
            self._token = self._fetch_token()
            return

    def refresh(self):
        if not self.__is_init:
            self._init()
        if self._token.is_expired():
            self._token = self._oauth_client.refresh_token(
                url=OAuth2Service.__OAUTH2_REFRESH_TOKEN_URL, refresh_token=self._token.get("refresh_token"))
            self._update_token(self._token)

    def get_id_token(self, force_refresh=False):
        if force_refresh or not self._id_token:
            self.refresh()
            return self._token.get("id_token")
        return self._id_token

    def fetch_access_token(self):
        self.refresh()
        return self._token.get("access_token")

    def fetch_refresh_token(self):
        self.refresh()
        return self._token.get("refresh_token")

    def get_email(self):
        pass

    def _fetch_token(self):
        if not os.path.exists(self._token_file):
            raise Exception(
                'Login credentials not found. please login and try again')
        else:
            with open(self._token_file, 'r') as fh:
                token = json.load(fh)
            return OAuth2Token.from_dict(token)

    def _update_token(self, token):
        with open(self._token_file, 'w') as fh:
            json.dump(token, fh)

    @staticmethod
    def get_oauth_client():
        oauth = OAuth()
        oauth.register(
            name=OAuth2Service.__OAUTH2_PROVIDER,
            client_id=OAuth2Service.__OAUTH2_CLIENT_ID,
            client_secret=OAuth2Service.__OAUTH2_CLIENT_SECRET,
            authorize_url=OAuth2Service.__OAUTH2_AUTHORIZE_URL,
            authorize_params=OAuth2Service.__OAUTH2_AUTHORIZE_PARAMS,
            refresh_token_url=OAuth2Service.__OAUTH2_REFRESH_TOKEN_URL,
            refresh_token_params=OAuth2Service.__OAUTH2_REFRESH_TOKEN_PARAMS,
            access_token_url=OAuth2Service.__OAUTH2_ACCESS_TOKEN_URL,
            access_token_params=OAuth2Service.__OAUTH2_ACCESS_TOKEN_PARAMS,
            client_kwargs={"scope": OAuth2Service.__OAUTH2_SCOPE},
            server_metadata_url=OAuth2Service.__OAUTH2_OPEN_ID_URL
            # token functions
        )
        return oauth

    def login(self):
        login(OAuth2Service.get_oauth_client(), OAuth2Service.__OAUTH2_PROVIDER, OAuth2Service.__OAUTH2_REDIRECT_URI,
              OAuth2Service.__OAUTH2_TOKEN_FILE)

    def logout(self):
        logout(OAuth2Service.__OAUTH2_TOKEN_FILE)

    @staticmethod
    def validate_spec(config):
        # OAuth2 Specs
        assert 'OAUTH2' in dir(config), "\n- configuration \"oauth2\" not found in config.yaml"
        assert 'PROVIDER' in dir(config.OAUTH2), "\n- configuration \"provider\" not found in config.yaml"
        assert 'AUTHORIZE_URL' in dir(config.OAUTH2), "\n- configuration \"authorize_params\" not found in config.yaml"
        assert 'AUTHORIZE_PARAMS' in dir(config.OAUTH2), "\n- configuration \"authorize_params\" not found in config.yaml"
        assert 'ACCESS_TOKEN_URL' in dir(config.OAUTH2), "\n- configuration \"access_token_url\" not found in config.yaml"
        assert 'ACCESS_TOKEN_PARAMS' in dir(config.OAUTH2), "\n- configuration \"access_token_params\" not found in config.yaml"
        assert 'REFRESH_TOKEN_URL' in dir(config.OAUTH2), "\n- configuration \"refresh_token_url\" not found in config.yaml"
        assert 'REFRESH_TOKEN_PARAMS' in dir(config.OAUTH2), "\n- configuration \"refresh_token_params\" not found in config.yaml"
        assert 'SCOPE' in dir(config.OAUTH2), "\n- configuration \"scope\" not found in config.yaml"
        assert 'OPEN_ID_URL' in dir(config.OAUTH2), "\n- configuration \"open_id_url\" not found in config.yaml"
