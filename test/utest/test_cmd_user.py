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
from sdlib.cmd.keyword_args import KeywordArguments

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                    os.path.abspath(__file__)))))

from sdlib.cmd.user.cmd import User

from test.utest import SdUtilTestCase


class TestCmdUser(SdUtilTestCase):
    def test_execute(self):

        cmd = User(None)

        with patch('sdlib.cmd.helper.CMDHelper.cmd_help'):

            args = []
            with self.assertRaises(Exception):
                cmd.execute(args, KeywordArguments())

            with patch('sdlib.api.seismic_store_service.SeismicStoreService.user_add'):

                args = ['add']
                with self.assertRaises(Exception):
                    cmd.execute(args, KeywordArguments())

                args = ['add', 'user']
                with self.assertRaises(Exception):
                    cmd.execute(args, KeywordArguments())

                args = ['add', 'user@domain.com']
                with self.assertRaises(Exception):
                    cmd.execute(args, KeywordArguments())

                args = ['add', 'user@domain.com', 'sd://tnx01']
                with self.assertRaises(Exception):
                    cmd.execute(args, KeywordArguments())

                args = ['add', 'user@domain.com', 'sd://tnx01/spx01']
                with self.assertRaises(Exception):
                    cmd.execute(args, KeywordArguments())

                args = ['add', 'user@domain.com', 'sd://tnx01/spx01', 'generic_role']
                with self.assertRaises(Exception):
                    cmd.execute(args, KeywordArguments())

                args = ['add', 'user@domain.com', 'sd://tnx01/spx01', 'viewer']
                cmd.execute(args, KeywordArguments())

                args = ['add', 'user@domain.com', 'sdx://tnx01/spx01']
                with self.assertRaises(Exception):
                    cmd.execute(args, KeywordArguments())


            with patch('sdlib.api.seismic_store_service.SeismicStoreService.user_list'):

                args = ['list']
                with self.assertRaises(Exception):
                    cmd.execute(args, KeywordArguments())

                args = ['list', 'sd://tnx01']
                with self.assertRaises(Exception):
                    cmd.execute(args, KeywordArguments())

            with patch('sdlib.api.seismic_store_service.SeismicStoreService.user_list', return_value=['item0', 'item1']):

                args = ['list', 'sd://tnx01/spx01']
                cmd.execute(args, KeywordArguments())

            with patch('sdlib.api.seismic_store_service.SeismicStoreService.user_remove'):

                args = ['remove']
                with self.assertRaises(Exception):
                    cmd.execute(args, KeywordArguments())

                args = ['remove', 'user']
                with self.assertRaises(Exception):
                    cmd.execute(args, KeywordArguments())

                args = ['remove', 'user@email.com']
                with self.assertRaises(Exception):
                    cmd.execute(args, KeywordArguments())

                args = ['remove', 'user@email.com', 'sd://tnx01']
                with self.assertRaises(Exception):
                    cmd.execute(args, KeywordArguments())

                args = ['remove', 'user@email.com', 'sd://tnx01/spx01']
                cmd.execute(args, KeywordArguments())

            # with patch('sdlib.api.seismic_store_service.SeismicStoreService.user_remove', return_value='OK'):


            args = ['roles']
            with self.assertRaises(Exception):
                cmd.execute(args, KeywordArguments())

            with patch('sdlib.api.seismic_store_service.SeismicStoreService.user_roles', return_value={'roles': [['a', 'b']]}):

                args = ['roles', 'sd://tnx01']
                cmd.execute(args, KeywordArguments())

            with patch('sdlib.api.seismic_store_service.SeismicStoreService.user_roles', return_value={'roles': None}):

                args = ['roles', 'sd://tnx01']
                cmd.execute(args, KeywordArguments())

            args = ['generic']
            with self.assertRaises(Exception):
                cmd.execute(args, KeywordArguments())

            args = ['roles', 'sd://tnx01/spx01']
            with self.assertRaises(Exception):
                cmd.execute(args, KeywordArguments())
