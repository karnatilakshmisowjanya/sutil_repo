# -*- coding: utf-8 -*-
# Copyright 2017-2023, Schlumberger
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
from sdlib.shared.config import Config


@AuthFactory.register(provider="e2e")
class SAuthService(AuthService):

    def __init__(self, idtoken=None):
        self.__custom_idtoken = idtoken

    def get_id_token(self):

        if self.__custom_idtoken:
            return self.__custom_idtoken
        
        raise Exception('\nToken must be provided by user for e2e')

    def login(self):
        pass

    def logout(self):
        pass

    def get_service_account_file(self):
        return "Null"
