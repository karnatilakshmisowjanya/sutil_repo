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


from sdlib.cmd.version.cmd import Version
import sys
import os
from mock import patch
from sdlib.cmd.keyword_args import KeywordArguments

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)))))

from test.utest import SdUtilTestCase


class TestCmdVersion(SdUtilTestCase):
    def test_execute(self):

        cmd = Version(None)

        with patch('sdlib.cmd.helper.CMDHelper.cmd_help'):

            versionFile = os.path.abspath(
                os.path.join(os.path.dirname(__file__), '../../.version'))

            if os.path.isfile(versionFile):
                os.remove(versionFile)

            with self.assertRaises(Exception):
                cmd.execute([], KeywordArguments())

            with open(versionFile, 'w') as fx:
                fx.write('1.0.0')

            cmd.execute([], KeywordArguments())

            if os.path.isfile(versionFile):
                os.remove(versionFile)
