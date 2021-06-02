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

from sdlib.auth.auth_service import AuthService, AuthFactory

@AuthFactory.register(provider="default")
class DefaultAuthService(AuthService):
    # initialize provider configurations
    def __init__(self, idtoken=None):
        self.idtoken = idtoken
    
    # get the idtoken
    def get_id_token(self):
        
        if self.idtoken == None:
            # generate a JWT Token
            raise Exception("\nPlease generate and pass a JWT Token with the '--idtoken=<token>' CLI parameter")
        return self.idtoken

    # refresh the idtoken
    def refresh(self):
        raise NotImplementedError()

    # login credentials
    def login(self):
        raise NotImplementedError()

    # logout credentials
    def logout(self):
        raise NotImplementedError()

    def get_service_account_file(self):
        raise NotImplementedError()

    @staticmethod
    def validate_spec(config):
        """
        A method to validate configuration specs

        :param config: Config
        :return: None; raises Assertion Exception
        """
        raise NotImplementedError()
