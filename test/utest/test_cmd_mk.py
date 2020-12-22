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
import io
from mock import patch

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                    os.path.abspath(__file__)))))

from sdlib.cmd.mk.cmd import Mk
from sdlib.cmd.keyword_args import KeywordArguments

from test.utest import SdUtilTestCase


class StringIO(io.StringIO):
    def __init__(self, value):
        self.value = value
        self.cnt = -1
        io.StringIO.__init__(self, None)

    def readline(self):
        if isinstance(self.value, list):
            self.cnt = self.cnt + 1
            return self.value[min(self.cnt, len(self.value) -1 )]
        else:
            return self.value


def stub_stdin(inputs):
    sys.stdin = StringIO(inputs)


class TestCmdMk(SdUtilTestCase):
    def setUp(self):
        patcher = patch("sdlib.api.seismic_store_service.SeismicStoreService.get_cloud_provider", lambda x, y: "google")
        self.mock_provider = patcher.start()
        self.addCleanup(patcher.stop)

    def test_execute(self):

        cmd = Mk(None)

        with patch('sdlib.cmd.helper.CMDHelper.cmd_help'):

            args = []
            with self.assertRaises(Exception):
                cmd.execute(args, KeywordArguments())

            with patch('sdlib.api.seismic_store_service.SeismicStoreService.tenant_register'):

                args = ['sd://tnx01']
                with self.assertRaises(Exception):
                    cmd.execute(args, KeywordArguments())

                args = ['sd://tnx01', 'gpcid@domain']
                with self.assertRaises(Exception):
                    cmd.execute(args, KeywordArguments())

                args = ['sd://tnx01', 'gpcid']
                with self.assertRaises(Exception):
                    cmd.execute(args, KeywordArguments())

                args = ['sd://tnx01', 'gpcid', 'user']
                with self.assertRaises(Exception):
                    cmd.execute(args, KeywordArguments())

                args = ['sd://tnx01', 'gpcid', 'esd', 'user@domain.com']
                with self.assertRaises(Exception):
                    cmd.execute(args, KeywordArguments())

            with patch('sdlib.api.seismic_store_service.SeismicStoreService.create_subproject'):
                
                with patch('sdlib.api.providers.google.storage_service.GoogleStorageService.get_storage_regions', return_value=['a', 'b', 'c']):

                    args = ['sd://tnx01/spx01']
                    with self.assertRaises(Exception):
                        cmd.execute(args, KeywordArguments())

                    args = ['sd://tnx01/spx01', 'user']
                    with self.assertRaises(Exception):
                        cmd.execute(args, KeywordArguments())

                    args = ['sd://tnx01/spx01', 'user@domain.com', 'ltag']
                    with self.assertRaises(Exception):
                        stub_stdin('x')
                        cmd.execute(args, KeywordArguments())

                    args = ['sd://tnx01/spx01', 'user@domain.com', 'ltag']
                    with self.assertRaises(Exception):
                        stub_stdin('0')
                        cmd.execute(args, KeywordArguments())

                    args = ['sd://tnx01/spx01', 'user@domain.com', 'ltag']
                    stub_stdin('1')
                    cmd.execute(args, KeywordArguments())

                    args = ['sd://tnx01/spx01', 'user@domain.com', 'ltag']
                    stub_stdin('2')
                    cmd.execute(args, KeywordArguments())

                    args = ['sd://tnx01/spx01', 'user@domain.com', 'ltag']
                    stub_stdin('3')
                    cmd.execute(args, KeywordArguments())

                    args = ['sd://tnx01/spx01', 'user@domain.com', 'ltag']
                    with self.assertRaises(Exception):
                        stub_stdin(['1', '0'])
                        cmd.execute(args, KeywordArguments())

                    args = ['sd://tnx01/spx01', 'user@domain.com', 'ltag']
                    with self.assertRaises(Exception):
                        stub_stdin(['1', 'x'])
                        cmd.execute(args, KeywordArguments())

            args = ['sdx://']
            with self.assertRaises(Exception):
                cmd.execute(args, KeywordArguments())