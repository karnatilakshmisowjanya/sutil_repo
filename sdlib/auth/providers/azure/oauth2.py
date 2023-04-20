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
import base64
import logging
import os
import json
import time
import requests

from authlib.integrations.requests_client import OAuth2Session
from authlib.oauth2.rfc6749.wrappers import OAuth2Token

from sdlib.shared.config import Config
from sdlib.auth.auth_service import AuthService, AuthFactory

from .config import Oauth2Configuration
from .login import login
from .logout import logout


@AuthFactory.register(provider="azure")
class OAuth2Service(AuthService):
    """
    A wrapper class for any OAuth2 provider based on Authlib
    https://docs.authlib.org/en/stable/index.html
    """

    def __init__(self, idtoken=None):

        self.__configuration = Oauth2Configuration(Config.get_auth_provider_configurations())

        self.__user_credential_loaded = False
        self.__custom_idtoken = idtoken
        self.__token = None
        self._oauth_client = OAuth2Session(
            client_id=self.__configuration.oauth2_client_id,
            client_secret=self.__configuration.oauth2_client_secret,
            scope=self.__configuration.oauth2_scopes,
            redirect_uri=self.__configuration.oauth2_redirect_uri,
            token=None
        )

    def load_user_credentials(self):
        if not os.path.exists(self.__configuration.token_file):
            raise Exception('Login credentials not found. please login and try again')
        else:
            with open(self.__configuration.token_file, 'r') as fh:
                token = json.load(fh)
            self.__token = OAuth2Token.from_dict(token)
        self.__user_credential_loaded = True

    def get_id_token(self):
        
        if self.__custom_idtoken:
            return self.__custom_idtoken

        if not self.__user_credential_loaded:
            self.load_user_credentials()

        payload = self.__token
        if int(payload['expiration']) < int(time.time()):
            if self.__configuration.force_refresh_token == "true" and \
                    int(payload["sdutil_auth_session_end_time"]) < int(time.time()):
                logging.info("refreshing the access token as its expired")
                self.refresh()
            else:
                raise Exception('\nLogin credentials have expired and either the refresh mechanism is not enabled or '
                                'the sdutil session has timed out. Login to the application via "sdutil auth login" '
                                'and try again')
        

        return self.__token.get("access_token")

    def refresh(self):
        if self.__token.is_expired():
            self.__token = self._oauth_client.refresh_token(
                url=self.__configuration.oauth2_authorize_url, refresh_token=self.__token.get("refresh_token"))
            self.__token["expiration"] = int(self.__token["expires_in"]) + time.time()
            self.__token["sdutil_auth_session_end_time"] = int(self.__token["expiration"]) + self.__configuration.sdutil_session_timeout * 3600
        with open(self.__configuration.token_file, 'w') as fh:
            json.dump(self.__token, fh)

    def login(self):
        login(self.__configuration)

    def logout(self):
        logout(self.__configuration)

    def get_service_account_file(self=None):
        return self.__configuration.service_account_file


