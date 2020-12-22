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
from mock import patch, Mock

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)))))

from sdlib.api.seismic_store_service import SeismicStoreService

from test.utest import SdUtilTestCase


class TestApiSeismicStore(SdUtilTestCase):

    def mock_response(self, status=200, content="CONTENT", headers=None, json_data=None, text=None,
                      raise_for_status=None):
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
        self.ss = SeismicStoreService(self.mock_auth)

    @patch('requests.post')
    def test_create_subproject(self, mock_request_post):
        mock_request_post.return_value = self.mock_response()
        self.assertEqual(self.ss.create_subproject('tnx01', 'spx01', 'user@email.com', 'gcsclass', 'gcsloc', 'ltag'),
                         None)

        with self.assertRaises(Exception):
            mock_request_post.return_value = self.mock_response(status=404)
            self.ss.create_subproject('tnx01', 'spx01', 'user@email.com', 'gcsclass', 'gcsloc', 'ltag')

    @patch('requests.get')
    def test_get_subproject(self, mock_request_get):
        res_get = {'message': 'mex'}
        mock_request_get.return_value = self.mock_response(json_data=res_get)
        self.assertEqual(self.ss.get_subproject('tnx01', 'spx01'), res_get)

        with self.assertRaises(Exception):
            mock_request_get.return_value = self.mock_response(status=404)
            self.ss.get_subproject('tnx01', 'spx01')

    @patch('requests.get')
    def test_ls(self, mock_request_get):
        res_ls = {'message': 'mex'}
        mock_request_get.return_value = self.mock_response(json_data=res_ls)
        self.assertEqual(self.ss.ls('sd://tnx01/spx01/a/b/c/'), res_ls)

        with self.assertRaises(Exception):
            mock_request_get.return_value = self.mock_response(status=404)
            self.ss.ls('sd://tnx01/spx01/a/b/c/')

    @patch('requests.post')
    def test_dataset_register(self, mock_request_post):
        res_dataset_register = {'message': 'mex'}
        mock_request_post.return_value = self.mock_response(json_data=res_dataset_register)
        self.assertEqual(self.ss.dataset_register('sd://tnx01/spx01/a/b/c/'), res_dataset_register)

        with self.assertRaises(Exception):
            mock_request_post.return_value = self.mock_response(status=404)
            self.ss.dataset_register('sd://tnx01/spx01/a/b/c/', 'zgy')

    @patch('requests.get')
    def test_dataset_get(self, mock_request_get):
        res_dataset_get = {'message': 'mex'}
        mock_request_get.return_value = self.mock_response(json_data=res_dataset_get)
        self.assertEqual(self.ss.dataset_get('sd://tnx01/spx01/a/b/c/'), res_dataset_get)

        with self.assertRaises(Exception):
            mock_request_get.return_value = self.mock_response(status=404)
            self.ss.dataset_get('sd://tnx01/spx01/a/b/c/')

    @patch('requests.patch')
    def test_dataset_patch(self, mock_request_patch):
        dataset_patch = {'message': 'mex'}
        mock_request_patch.return_value = self.mock_response(json_data=dataset_patch)
        self.assertEqual(self.ss.dataset_patch('sd://tnx01/spx01/a/b/c/', 'patch'), dataset_patch)

        with self.assertRaises(Exception):
            mock_request_patch.return_value = self.mock_response(status=404)
            self.ss.dataset_patch('sd://tnx01/spx01/a/b/c/', 'patch')

    @patch('requests.delete')
    def test_dataset_delete(self, mock_request_delete):
        mock_request_delete.return_value = self.mock_response()
        self.assertEqual(self.ss.dataset_delete('sd://tnx01/spx01/a/b/c/'), None)

        with self.assertRaises(Exception):
            mock_request_delete.return_value = self.mock_response(status=404)
            self.ss.dataset_delete('sd://tnx01/spx01/a/b/c/')

    @patch('requests.post')
    def test_user_register(self, mock_request_post):
        mock_request_post.return_value = self.mock_response(status=200)
        self.assertEqual(self.ss.user_register('user@email.com'), 200)

        with self.assertRaises(Exception):
            mock_request_post.return_value = self.mock_response(status=404)
            self.ss.user_register('user@email.com')

    @patch('requests.put')
    def test_user_add(self, mock_request_put):
        mock_request_put.return_value = self.mock_response(status=200)
        self.assertEqual(self.ss.user_add('sd://tnx01/spx01', 'user@email.com', 'role'), None)

        with self.assertRaises(Exception):
            mock_request_put.return_value = self.mock_response(status=404)
            self.ss.user_add('sd://tnx01', 'user@email.com')

    @patch('requests.get')
    def test_user_list(self, mock_request_get):
        mock_request_get.return_value = self.mock_response(status=200)
        self.assertEqual(self.ss.user_list('sd://tnx01/spx01'), None)

        with self.assertRaises(Exception):
            mock_request_get.return_value = self.mock_response(status=404)
            self.ss.user_list('sd://tnx01/spx01')

    @patch('requests.delete')
    def test_user_remove(self, mock_request_delete):
        mock_request_delete.return_value = self.mock_response(status=200)
        self.assertEqual(self.ss.user_remove('sd://tnx01/spx01', 'user@email.com'), None)

        with self.assertRaises(Exception):
            mock_request_delete.return_value = self.mock_response(status=404)
            self.ss.user_remove('sd://tnx01/spx01', 'user@email.com')

    @patch('requests.put')
    def test_user_system_admin_add(self, mock_request_put):
        mock_request_put.return_value = self.mock_response(status=200)
        self.assertEqual(self.ss.user_system_admin_add('user@email.com'), None)

        with self.assertRaises(Exception):
            mock_request_put.return_value = self.mock_response(status=404)
            self.ss.user_system_admin_add('user@email.com')

    @patch('requests.get')
    def test_set_legaltag(self, mock_request_get):
        mock_request_get.return_value = self.mock_response(status=200)
        self.assertEqual(self.ss.set_legatag('ltag'), None)

        with self.assertRaises(Exception):
            mock_request_get.return_value = self.mock_response(status=404)
            self.ss.set_legatag('ltag')

    @patch('requests.get')
    def test_user_roles(self, mock_request_get):
        res_user_roles = {'message': 'mex'}
        mock_request_get.return_value = self.mock_response(json_data=res_user_roles)
        self.assertEqual(self.ss.user_roles('sd://tnx01'), res_user_roles)

        with self.assertRaises(Exception):
            mock_request_get.return_value = self.mock_response(status=404)
            self.ss.user_roles('sd://tnx01')

    @patch('requests.get')
    def test_app_list(self, mock_request_get):
        res_app_list = {'message': 'mex'}
        mock_request_get.return_value = self.mock_response(json_data=res_app_list)
        self.assertEqual(self.ss.app_list('sd://tnx01'), res_app_list)

        with self.assertRaises(Exception):
            mock_request_get.return_value = self.mock_response(status=404)
            self.ss.app_list('sd://tnx01')

    @patch('requests.get')
    def test_apptrusted_list(self, mock_request_get):
        res_apptrusted_list = {'message': 'mex'}
        mock_request_get.return_value = self.mock_response(json_data=res_apptrusted_list)
        self.assertEqual(self.ss.apptrusted_list('sd://tnx01'), res_apptrusted_list)

        with self.assertRaises(Exception):
            mock_request_get.return_value = self.mock_response(status=404)
            self.ss.apptrusted_list('sd://tnx01')

    @patch('requests.post')
    def test_app_register(self, mock_request_post):
        mock_request_post.return_value = self.mock_response(status=200)
        self.assertEqual(self.ss.app_register('service@email.com', 'sd://tnx01'), 200)

        with self.assertRaises(Exception):
            mock_request_post.return_value = self.mock_response(status=404)
            self.ss.app_register('service@email.com', 'sd://tnx01')

    @patch('requests.post')
    def test_apptrusted_register(self, mock_request_post):
        mock_request_post.return_value = self.mock_response(status=200)
        self.assertEqual(self.ss.apptrusted_register('service@email.com', 'sd://tnx01'), 200)

        with self.assertRaises(Exception):
            mock_request_post.return_value = self.mock_response(status=404)
            self.ss.apptrusted_register('service@email.com', 'sd://tnx01')
