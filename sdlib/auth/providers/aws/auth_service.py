# -*- coding: utf-8 -*-
# Copyright 2017-2019, Schlumberger
# Amazon Web Services 2021
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
from __future__ import print_function

import os
import stat
import boto3
import getpass
import pickle

from sdlib.auth.auth_service import AuthService, AuthFactory
from sdlib.shared.config import Config

from .config import AwsAuthConfig

@AuthFactory.register(provider="aws")
class AwsAuthService(AuthService):
    # initialize provider configurations
    def __init__(self, idtoken=None):
        self.__custom_idtoken = idtoken

        if not self.__custom_idtoken:
            self.__configuration = AwsAuthConfig(Config.get_auth_provider_configurations())
            self.__token = None
            self.__refresh_token = None

            self.__user_credential_loaded = False
            
            self._aws_session = boto3.session.Session(profile_name=self.__configuration.aws_profile)
            self._cognito_client = self._aws_session.client('cognito-idp')
    
    # get the idtoken
    def get_id_token(self, force_refresh:bool=False):
        if self.__custom_idtoken:
            return self.__custom_idtoken

        if not self.__user_credential_loaded:
            self.load_user_credentials()
        
        return self.__token
    
    def load_user_credentials(self):
        if not os.path.exists(self.__configuration.token_file):
            raise Exception('Login credentials not found. please login and try again')
        else:
            with open(self.__configuration.token_file, 'rb') as fh:
                token = pickle.load(fh)
            self.__configuration.cognito_user = token['username']
            self.__token = token['access_token']
            self.__refresh_token = token['refresh_token']
            print(f'Loaded cached credentials for {self.__configuration.cognito_user}')
        self.__user_credential_loaded = True

    # refresh the idtoken
    def refresh(self):
        self.login()

    # login credentials
    def login(self):
        # Make sure we have username and password
        if not self.__configuration.aws_profile: 
            self.__configuration.cognito_password = input('Enter your AWS profile for the AWS account that hosts the OSDU instance: ')

        if not self.__configuration.cognito_user: 
            self.__configuration.cognito_user = input('Enter your Cognito username: ')

        if not self.__configuration.cognito_password: 
            self.__configuration.cognito_password = getpass.getpass(f'({self.__configuration.cognito_user}) Enter your Cognito password: ')

        # Generate access token from Cognito
        response = self._cognito_client.initiate_auth(
            AuthFlow='USER_PASSWORD_AUTH',
            ClientId=self.__configuration.cognito_client_id,
            AuthParameters={'USERNAME': self.__configuration.cognito_user, 'PASSWORD': self.__configuration.cognito_password}
        )
        access_token = response['AuthenticationResult']['AccessToken']
        refresh_token = response['AuthenticationResult']['RefreshToken']

        # ensure the directory exist if not create it
        if not os.path.isdir(self.__configuration.token_file_dir):
            os.mkdir(self.__configuration.token_file_dir)

        # write the file token
        with open(self.__configuration.token_file, "wb") as fh:
            pickle.dump({
                "username": self.__configuration.cognito_user,
                "access_token": access_token,
                "refresh_token": refresh_token
            }, fh)
            
        # Help prevent others from stealing the credentials. CAVEAT: chmod has little effect on windows.
        os.chmod(self.__configuration.token_file, stat.S_IRUSR | stat.S_IWUSR)

    # logout credentials
    def logout(self):
        try:
            os.remove(self.__configuration.token_file)
        except OSError:
            pass

    def get_service_account_file(self):
        return self.__configuration.service_account_file
