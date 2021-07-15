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

from sdlib.api.dataset import Dataset
from sdlib.cmd.stat.cmd import Stat
from sdlib.cmd.keyword_args import KeywordArguments
import sys
import os

from mock import patch

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)))))

from test.utest import SdUtilTestCase


class TestCmdStat(SdUtilTestCase):

    def test_execute(self):

        cmd = Stat(None)

        with self.assertRaises(Exception):
            args = ['sd://']
            cmd.execute(args, KeywordArguments())

        with patch('sdlib.cmd.helper.CMDHelper.cmd_help'):

            t = {
                'esd': 'tenant-esd',
                'gcpid': 'tenant-gcpid'
            }
            with patch('sdlib.api.seismic_store_service.SeismicStoreService.get_tenant', return_value=t):
                args = ['sd://tnx01']
                cmd.execute(args, KeywordArguments())

            sp = {
                'storage_class': 'storage_class',
                'storage_location': 'storage_location',
                'access_policy': 'uniform'
            }
            with patch('sdlib.api.seismic_store_service.SeismicStoreService.get_subproject', return_value=sp):
                args = ['sd://tnx01/spx01']
                cmd.execute(args, KeywordArguments())

            sp['ltag'] = 'ltag'
            sp['access_policy'] = 'uniform'
            with patch('sdlib.api.seismic_store_service.SeismicStoreService.get_subproject', return_value=sp):
                args = ['sd://tnx01/spx01']
                cmd.execute(args, KeywordArguments())

            ds = Dataset()
            ds.dstype = 'zgy'
            ds.tenant = 'tnx01'
            ds.subproject = 'spx01'
            ds.path = '/a/b/c/'
            ds.name = 'dsx01'
            ds.created_by = 'me@domain.com'
            ds.created_date = '01 Jan 2018'
            ds.filemetadata = {'size': 1024}

            with patch('sdlib.api.dataset.Dataset.from_json', return_value=ds):
                with patch('sdlib.api.seismic_store_service.SeismicStoreService.dataset_get'):
                    args = ['sd://tnx01/spx01/a/b/c/dsx01']
                    cmd.execute(args, KeywordArguments())

                    ds.filemetadata = {}
                    args = ['sd://tnx01/spx01/a/b/c/dsx01']
                    cmd.execute(args, KeywordArguments())

                    ds.filemetadata = None
                    args = ['sd://tnx01/spx01/a/b/c/dsx01']
                    cmd.execute(args, KeywordArguments())

                    ds.dstype = None
                    args = ['sd://tnx01/spx01/a/b/c/dsx01']
                    cmd.execute(args, KeywordArguments())
