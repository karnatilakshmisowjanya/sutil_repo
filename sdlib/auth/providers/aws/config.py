
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
#   aws: '{"provider": "#{aws.provider}#", "cognito_client_id": "#{aws.cognito_client_id}#"}'

class AwsAuthConfig(object):

    def __init__(self, configuration):

        assert 'provider' in configuration , "\nThe \"provider\" configuration has not been found in the \"auth_provider:aws\" section of the config.yaml"
        assert 'cognito_client_id' in configuration , "\nThe \"cognito_client_id\" configuration has not been found in the \"auth_provider:aws\" section of the config.yaml"
       
        self.cognito_provider = configuration['provider']
        self.cognito_client_id = configuration['cognito_client_id']
        
        # We do not throw or prompt for these as they are optionally collected when needed
        self.aws_profile = os.getenv("AWS_PROFILE")
        self.cognito_user = os.getenv("COGNITO_USER")
        self.cognito_password = os.getenv("COGNITO_PASSWORD")

        self.token_file_name = "auth.token"
        self.token_file_dir = os.path.join(os.path.expanduser("~"), Config.HOME)
        self.token_file = os.path.join(self.token_file_dir, self.token_file_name)
        self.service_account_file_name = "service_auth_account.token"
        self.service_account_file = os.path.join(self.token_file_dir, self.service_account_file_name)

