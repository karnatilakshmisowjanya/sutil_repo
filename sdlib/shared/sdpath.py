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


from six.moves import urllib


class SDPath(object):

    def __init__(self, sdpath):

        self.tenant = None
        self.subproject = None
        self.path = None
        self.dataset = None

        sdpath = str(sdpath)

        if 'sd://' in sdpath:

            sdpath = sdpath.replace('sd://', '')

            if sdpath.count('/') == 0:  # tenant only
                self.tenant = sdpath
            elif sdpath.count('/') == 1:  # subproject only
                splitpath = sdpath.split('/')
                self.tenant = splitpath[0]
                self.subproject = splitpath[1]
            elif sdpath.count('/') == 2:  # path missing
                splitpath = sdpath.split('/')
                self.tenant = splitpath[0]
                self.subproject = splitpath[1]
                self.path = urllib.parse.quote('/', safe='')
                self.dataset = splitpath[2]
            else:  # full
                splitpath = sdpath.split('/')
                self.tenant = splitpath[0]
                self.subproject = splitpath[1]
                self.dataset = urllib.parse.quote(splitpath[-1], safe='')
                self.path = '/'.join(splitpath[2:-1])
