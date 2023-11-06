
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
import re

from sdlib.shared.config import Config
import urllib.parse

# auth_provider:
#   oauth2: '{"provider": "#{oauth2.provider}#", "authorize_url": "#{oauth2.authorize_url}#", "authorize_params": "#{oauth2.authorize_params}#", "access_token_url": "#{oauth2.access_token_url}#", "access_token_params": "#{oauth2.access_token_params}#", "refresh_token_url": "#{oauth2.refresh_token_url}#", "refresh_token_params": "#{oauth2.refresh_token_params}#", "open_id_url": "#{oauth2.open_id_url}#", "scope": "#{oauth2.scope}#"}'

class Oauth2Configuration(object):

    def __init__(self, configuration):

        assert 'provider' in configuration , "\nThe \"provider\" configuration has not been found in the \"auth_provider:oauth2\" section of the config.yaml"
        assert 'authorize_url' in configuration , "\nThe \"authorize_url\" configuration has not been found in the \"auth_provider:oauth2\" section of the config.yaml"
        assert 'authorize_params' in configuration , "\nThe \"authorize_params\" configuration has not been found in the \"auth_provider:oauth2\" section of the config.yaml"
        assert 'access_token_url' in configuration , "\nThe \"access_token_url\" configuration has not been found in the \"auth_provider:oauth2\" section of the config.yaml"
        assert 'access_token_params' in configuration , "\nThe \"access_token_params\" configuration has not been found in the \"auth_provider:oauth2\" section of the config.yaml"
        assert 'refresh_token_url' in configuration , "\nThe \"refresh_token_url\" configuration has not been found in the \"auth_provider:oauth2\" section of the config.yaml"
        assert 'refresh_token_params' in configuration , "\nThe \"refresh_token_params\" configuration has not been found in the \"auth_provider:oauth2\" section of the config.yaml"
        assert 'open_id_url' in configuration , "\nThe \"open_id_url\" configuration has not been found in the \"auth_provider:oauth2\" section of the config.yaml"
        assert 'scope' in configuration , "\nThe \"scope\" configuration has not been found in the \"auth_provider:oauth2\" section of the config.yaml"

        self.oauht2_provider = configuration['provider']
        self.oauht2_authorize_url = configuration['authorize_url']
        self.oauht2_authorize_params = configuration['authorize_params']
        self.oauht2_access_token_url = configuration['access_token_url']
        self.oauht2_access_token_params = configuration['access_token_params']
        self.oauht2_refresh_token_url = configuration['refresh_token_url']
        self.oauht2_refresh_token_param = configuration['refresh_token_params']
        self.oauht2_open_id_url = configuration['open_id_url']
        self.oauht2_scope = configuration['scope']
        self.redirect_url = configuration['redirect_url']

        self.oauth2_client_id = os.getenv("OAUTH2_CLIENT_ID")
        if not self.oauth2_client_id:
            raise Exception('\nOAUTH2_CLIENT_ID is required but have not been found in the environement.')

        self.oauth2_client_secret = os.getenv("OAUTH2_CLIENT_SECRET")
        if not self.oauth2_client_secret: 
            raise Exception('\nOAUTH2_CLIENT_SECRET is required but have not been found in the environement.')

        self.oauth2_client_redirect_url = os.getenv("OAUTH2_CLIENT_REDIRECT_URL")
        if not self.oauth2_client_redirect_url:
            raise Exception('\nOAUTH2_CLIENT_REDIRECT_URL is required but have not been found in the environement.')

        if not self.oauth2_client_redirect_url.endswith('/auth/callback'):
            raise Exception('\nThe redirect url must be of this "https://<host>:<port>/auth/callback"')

        self.oauth2_client_redirect_url_port = urllib.parse.urlparse(self.redirect_url).port if urllib.parse.urlparse(self.oauth2_client_redirect_url).port else 4300

        self.token_file_name = "auth.token"
        self.token_file_dir = os.path.join(os.path.expanduser("~"), Config.HOME)
        self.token_file = os.path.join(self.token_file_dir, self.token_file_name)
        self.service_account_file_name = "service_auth_account.token"
        self.service_account_file = os.path.join(self.token_file_dir, self.service_account_file_name)
