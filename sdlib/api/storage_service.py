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


from __future__ import print_function


class StorageFactory(type):
    provider_classes = {}

    @classmethod
    def register(cls, provider):
        def wrapper(klass):
            StorageFactory.provider_classes[provider] = klass
            return klass

        return wrapper

    @classmethod
    def build(cls, provider, *args, **kwargs):
        try:
            provider = provider.strip().lower()
            if provider == 'unknown':
                raise KeyError()

            klass = cls.provider_classes[provider]
        except KeyError:
            raise ValueError("No known class associated with %s" % provider)
        return klass(*args, **kwargs)


class StorageService(object):

    def __init__(self, auth, *args, **kwargs):
        self._auth = auth

    def upload(self, *args, **kwargs):
        raise NotImplementedError()

    def download(self, *args, **kwargs):
        raise NotImplementedError()
    
    def download_object(self, *args, **kwargs):
        raise NotImplementedError()