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

import os

from sdlib.cmd.cmd import SDUtilCMD


class Version(SDUtilCMD):

    def __init__(self, auth):
        self._auth = auth

    def execute(self, args, keyword_args):
        versionFile = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '../../../.version'))

        if os.path.isfile(versionFile):
            with open(versionFile, 'r') as fx:
                print('\n' + fx.read())
        else:
            raise Exception('\nNo version can be found in sdutil')
