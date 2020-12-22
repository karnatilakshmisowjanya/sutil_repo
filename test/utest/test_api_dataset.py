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


import os
import sys
import io

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                    os.path.abspath(__file__)))))

from test.utest import SdUtilTestCase
from sdlib.api.dataset import Dataset


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


class TestApiDataset(SdUtilTestCase):

    stub_stdin('fake-appkey-4-utest')
    def test_dataset(self):
        data = {
            'tenant':'tnx01',
            'subproject':'spx01',
            'path':'/a/b/c/',
            'name':'dsx01',
            'created_by':'user@domain.com',
            'type':'txt',
            'status': True,
            'created_date':'01/01/200 00:00:00',
            'last_modified_date':'01/01/200 00:00:00',
            'metadata': {'key': 'value'},
            'filemetadata':{'key': 'value'},
            'readonly': False,
            'gcsurl':'gs://bucket/folder',
        }
        ds = Dataset.from_json(data)
        self.assertEqual(ds.tenant, data['tenant'])
        self.assertEqual(ds.subproject, data['subproject'])
        self.assertEqual(ds.path, data['path'])                
        self.assertEqual(ds.name, data['name'])         
        self.assertEqual(ds.created_by, data['created_by'])         
        self.assertEqual(ds.dstype, data['type'])                                 
        self.assertEqual(ds.created_date, data['created_date'])
        self.assertEqual(ds.last_modified_date, data['last_modified_date'])
        self.assertEqual(ds.metadata, data['metadata'])
        self.assertEqual(ds.filemetadata, data['filemetadata'])
        self.assertEqual(ds.gcsurl, data['gcsurl'])
        self.assertEqual(ds.readonly, data['readonly'])
