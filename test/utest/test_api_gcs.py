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
from sdlib.api.providers.google import GoogleStorageService

import os
import sys
from mock import patch, Mock

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)))))

from test.utest import SdUtilTestCase


class TestApiGcs(SdUtilTestCase):

    def mock_response(self, status=200, content="CONTENT", headers=None, json_data=None, text=None, raise_for_status=None):
        mock_resp = Mock()
        mock_resp.raise_for_status = Mock(side_effect=raise_for_status)
        mock_resp.status_code = status
        mock_resp.content = content
        mock_resp.json = Mock(return_value=json_data)
        mock_resp.text = text
        mock_resp.headers = headers
        return mock_resp

    def setUp(self):
        self.mock_auth = Mock()
        self.mock_auth.get_id_token = lambda: '!-my-magic-id-token'
        self.gcs = GoogleStorageService(auth=self.mock_auth)
        self.ds = Dataset()
        self.ds.gcsurl = 'gs://bucket/folder'

    @patch('requests.delete')
    def test_object_delete(self, mock_request_delete):
        with patch('sdlib.api.seismic_store_service.SeismicStoreService.get_storage_access_token'):
            mock_request_delete.return_value = self.mock_response(status=204)
            self.assertEqual(self.gcs.object_delete('obj', self.ds), None)

            with self.assertRaises(Exception):
                mock_request_delete.return_value = self.mock_response(
                    status=404)
                self.gcs.object_delete('obj', self.ds)

    @patch('requests.post')
    def test_object_add(self, mock_request_post):
        with patch('sdlib.api.seismic_store_service.SeismicStoreService.get_storage_access_token'):
            mock_request_post.return_value = self.mock_response(status=200)
            self.assertEqual(self.gcs.object_add('obj', self.ds), None)

            with self.assertRaises(Exception):
                mock_request_post.return_value = self.mock_response(status=404)
                self.gcs.object_add('obj', self.ds)

    @patch('requests.post')
    def test_object_upload(self, mock_request_post):
        with patch('sdlib.api.seismic_store_service.SeismicStoreService.get_storage_access_token'):
            mock_request_post.return_value = self.mock_response(status=200)
            self.assertEqual(self.gcs.object_upload(
                'bucket', 'obj', 'data', 'tnx01', 'spx01'), None)

            with self.assertRaises(Exception):
                mock_request_post.return_value = self.mock_response(status=404)
                self.gcs.object_upload(
                    'bucket', 'obj', 'data', 'tnx01', 'spx01')

    @patch('requests.get')
    def test_object_download(self, mock_request_get):
        with patch('sdlib.api.seismic_store_service.SeismicStoreService.get_storage_access_token'):
            mock_request_get.return_value = self.mock_response(
                status=200, content='content')
            self.assertEqual(self.gcs.object_download(
                'bucket', 'obj', 'tnx01', 'spx01'), 'content')

            with self.assertRaises(Exception):
                mock_request_get.return_value = self.mock_response(status=404)
                self.gcs.object_download('bucket', 'obj', 'tnx01', 'spx01')

    @patch('requests.get')
    def test_object_attribute(self, mock_request_get):
        with patch('sdlib.api.seismic_store_service.SeismicStoreService.get_storage_access_token'):
            res_object_attribute = {'attribute': 'value'}
            mock_request_get.return_value = self.mock_response(
                status=200, json_data=res_object_attribute)
            self.assertEqual(self.gcs.object_attribute(
                'bucket', 'obj', 'attribute', 'tnx01', 'spx01'), res_object_attribute['attribute'])

            with self.assertRaises(Exception):
                mock_request_get.return_value = self.mock_response(status=404)
                self.gcs.object_attribute(
                    'bucket', 'obj', 'tnx01', 'attribute', 'spx01')

    def test_object_size(self):
        with patch('sdlib.api.providers.google.GoogleStorageService.object_attribute'):
            self.gcs.object_size('bucket', 'object', 'tnx01', 'spx01')
