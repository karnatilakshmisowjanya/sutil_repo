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

import abc


class AuthFactory(type):
    provider_classes = {}

    @classmethod
    def register(cls, provider):
        def wrapper(klass):
            AuthFactory.provider_classes[provider] = klass
            return klass

        return wrapper

    @classmethod
    def build(cls, provider, idtoken, *args, **kwargs):
        try:
            provider = provider.strip().lower()
            klass = cls.provider_classes[provider]
        except KeyError:
            raise ValueError("No known auth class associated with %s" % provider)
        return klass(idtoken, *args, **kwargs)


class AuthService(abc.ABC):

    @abc.abstractmethod
    def __init__(self, idtoken=None):
        pass

    @abc.abstractmethod
    def get_id_token(self):
        pass

    @abc.abstractmethod
    def login(self):
        pass

    @abc.abstractmethod
    def logout(self):
        pass

    @abc.abstractmethod
    def get_service_account_file():
        pass;