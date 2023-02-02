
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

# auth_provider:
#   oauth2: '{"provider": "#{oauth2.provider}#", "authorize_url": "#{oauth2.authorize_url}#", "authorize_params": "#{oauth2.authorize_params}#", "access_token_url": "#{oauth2.access_token_url}#", "access_token_params": "#{oauth2.access_token_params}#", "refresh_token_url": "#{oauth2.refresh_token_url}#", "refresh_token_params": "#{oauth2.refresh_token_params}#", "open_id_url": "#{oauth2.open_id_url}#", "scope": "#{oauth2.scope}#"}'

class Oauth2Configuration(object):

    def __init__(self, configuration):

        assert 'provider' in configuration , "\nThe \"provider\" configuration has not been found in the \"auth_provider:oauth2\" section of the config.yaml"
        assert 'authorize_url' in configuration , "\nThe \"authorize_url\" configuration has not been found in the \"auth_provider:oauth2\" section of the config.yaml"
        assert 'oauth_token_host_end' in configuration , "\nThe \"oauth_token_host_end\" configuration has not been found in the \"auth_provider:oauth2\" section of the config.yaml"
        assert 'scope_end' in configuration , "\nThe \"scope_end\" configuration has not been found in the \"auth_provider:oauth2\" section of the config.yaml"
        assert 'redirect_uri' in configuration , "\nThe \"redirect_uri\" configuration has not been found in the \"auth_provider:oauth2\" section of the config.yaml"
        assert 'login_grant_type' in configuration , "\nThe \"login_grant_type\" configuration has not been found in the \"auth_provider:oauth2\" section of the config.yaml"
        assert 'refresh_token' in configuration , "\nThe \"refresh_token\" configuration has not been found in the \"auth_provider:oauth2\" section of the config.yaml"
       
        self.oauht2_provider = configuration['provider']
        self.azure_authorize_url = configuration['authorize_url']
        self.oauht2_token_host_end = configuration['oauth_token_host_end']
        self.oauth2_redirect_uri = configuration["redirect_uri"]
        self.oauth2_login_grant_type = configuration["login_grant_type"]
        self.oauth2_refresh_token = configuration["refresh_token"]

        self.azure_tenant_id = os.getenv("AZURE_TENANT_ID")
        if not self.azure_tenant_id:
            raise Exception('\AZURE TENANT ID is required but have not been found in the environement.')

        self.oauth2_client_id = os.getenv("AZURE_CLIENT_ID")
        if not self.oauth2_client_id:
            raise Exception('\AZURE CLIENT ID is required but have not been found in the environement.')

        self.oauth2_client_secret = os.getenv("AZURE_CLIENT_SECRET")
        if not self.oauth2_client_secret:
            raise Exception('\AZURE CLIENT SECRET is required but have not been found in the environement.')

        
        self.oauht2_authorize_url = self.azure_authorize_url + self.azure_tenant_id + self.oauht2_token_host_end
        self.oauth2_scopes = self.oauth2_client_id + configuration["scope_end"]

        self.token_file_name = "auth.token"
        self.token_file_dir = os.path.join(os.path.expanduser("~"), Config.HOME)
        self.token_file = os.path.join(self.token_file_dir, self.token_file_name)
        self.service_account_file_name = "service_auth_account.token"
        self.service_account_file = os.path.join(self.token_file_dir, self.service_account_file_name)

