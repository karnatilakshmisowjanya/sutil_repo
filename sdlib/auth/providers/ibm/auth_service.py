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


class IbmAuthFactory(type):
    provider_classes = {}

    @classmethod
    def register(cls, provider):
        def wrapper(klass):
            IbmAuthFactory.provider_classes[provider] = klass
            return klass

        return wrapper

    @classmethod
    def build(cls, provider, *args, **kwargs):
        try:
            provider = provider.strip().lower()
            klass = cls.provider_classes[provider]
        except KeyError:
            raise ValueError("No known auth class associated with %s" % provider)
        return klass(*args, **kwargs)


class IbmAuthService(AuthService):

    def __init__(self, idtoken=None):
        pass

    def get_id_token(self):
        pass

    def login(self):
        pass

    def logout(self):
        pass

    def get_service_account_file(self):
        pass;
