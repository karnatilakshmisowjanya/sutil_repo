# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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
from sdlib.api.providers.aws.storage_service import AwsStorageService
import os
import sys
from mock import patch, Mock

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)))))

from test.utest import SdUtilTestCase

class TestApiAws(SdUtilTestCase):
    def setUp(self):
        self.auth_mock = Mock()
        self.aws = AwsStorageService(auth=self.auth_mock)
        self.aws._s3_client = Mock()
        self.aws._s3_resource = Mock()
        self.ds = Dataset()
        self.ds.gcsurl = 'bucket_name$$subproject_folder/dataset_folder'
        self.ds.filemetadata = {'nobjects': 1, 'size': 1}
        self.ds.tenant = 'tenant'
        self.ds.subproject = 'subproject'
        self.object_name = 'test_object'
        self.file_name = 'test_file.txt'
        self.cursize = 0
        self.bucket = 'bucket_name'
        self.obj = 2

        with open(self.file_name, 'w') as f:
            f.write("Test content")

    def tearDown(self):
        os.remove(self.file_name)

    @patch('sdlib.api.providers.aws.storage_service.S3Transfer')
    @patch('sdlib.api.providers.aws.storage_service.boto3.client')
    def test_upload(self, mock_boto3_client, mock_s3_transfer):
        mock_s3_transfer_instance = Mock()
        mock_s3_transfer.return_value = mock_s3_transfer_instance

        mock_s3_client = Mock()
        mock_boto3_client.return_value = mock_s3_client

        result = self.aws.upload(self.file_name, self.ds, self.object_name)

        self.assertEqual(result, {"num_of_objects": 1})

    @patch('sdlib.api.providers.aws.storage_service.boto3.client')
    def test_download(self, mock_boto3_client):
        mock_s3_client = Mock()
        mock_boto3_client.return_value = mock_s3_client

        self.aws.downloadObject = Mock(return_value=524288)  

        result = self.aws.download(self.file_name, self.ds)

        self.assertTrue(result)

    @patch('sdlib.api.providers.aws.storage_service.boto3.resource')
    @patch('sdlib.api.providers.aws.storage_service.boto3.client')
    def test_download_object(self, mock_boto3_client, mock_boto3_resource):
        # Mock S3 client and resource
        mock_s3_client = Mock()
        mock_boto3_client.return_value = mock_s3_client

        self.aws._s3_resource.Object.return_value.content_length = 12345
        # Mock get_object response
        mock_response = {
    'Body': [b'chunk1', b'chunk2', b'chunk3']  # Simulating the response body as chunks of bytes
        }   
        self.aws._s3_client.get_object.return_value = mock_response
        # Use a real file for local_file
        with open(self.file_name, 'wb') as local_file:
            objsize = self.aws.downloadObject(local_file, self.bucket, self.obj, self.ds, self.cursize)

        # Assertions
        self.assertEqual(objsize, 12345)


    @patch('boto3.resource')
    @patch('sdlib.api.providers.aws.storage_service.SeismicStoreService.get_storage_access_token')
    def test_get_s3_client(self,mock_get_storage_access_token, mock_boto3_resource):
        # Mock response from get_storage_access_token
        mock_get_storage_access_token.return_value = 'access_key:secret_key:session_token'

        # Mock boto3 resource
        mock_s3_resource = Mock()
        mock_boto3_resource.return_value = mock_s3_resource
        mock_s3_resource.meta.client = Mock()

        s3_client = self.aws.get_s3_client(self.aws, self.ds)

        self.assertIsNotNone(s3_client)


    def test_get_storage_regions(self):
        res = self.aws.get_storage_regions()
        self.assertEqual(res, ["us-east-1", "US-CENTRAL1"])

    def test_get_storage_classes(self):
        res = self.aws.get_storage_classes()
        self.assertEqual(res, ['REGIONAL'])
