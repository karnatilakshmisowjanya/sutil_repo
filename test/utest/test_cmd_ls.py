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


import sys
import os
from mock import patch

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                    os.path.abspath(__file__)))))

from sdlib.cmd.ls.cmd import Ls
from sdlib.cmd.keyword_args import KeywordArguments

from test.utest import SdUtilTestCase


class TestCmdLs(SdUtilTestCase):

    def test_execute(self):

        cmd = Ls(None)

        with patch('sdlib.cmd.helper.CMDHelper.cmd_help'):

            args = ['sdx://tnx01']
            with self.assertRaises(Exception):
                cmd.execute(args, KeywordArguments())

            with patch('sdlib.api.seismic_store_service.SeismicStoreService.status', return_value=[None, {'Service-Provider': 'any'}]):
                with patch('sdlib.api.seismic_store_service.SeismicStoreService.ls', return_value=['item']):
                    args = ['sd://tnx01/spx01/a/b/c/dsx01']
                    cmd.execute(args, KeywordArguments())
