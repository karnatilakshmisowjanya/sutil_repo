#  Copyright 2022 Google LLC
#  Copyright 2022 EPAM Systems
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

import boto3
from botocore.client import Config
from sdlib.api.providers.aws import AwsStorageService
from sdlib.api.storage_service import StorageFactory

@StorageFactory.register(provider="anthos")
class MinioStorageService(AwsStorageService):

    @staticmethod
    def get_s3_client(self, dataset):
        """create a new boto3 s3 resource object

        Args:
            dataset (sdlib.api.dataset.Dataset): the dataset object being handled

        Returns:
            boto3.resource.meta.client: a boto3 S3 client, created from an s3 resource
        """

        response = self._seistore_svc.get_storage_access_token(tenant=dataset.tenant, subproject=dataset.subproject,readonly=False)

        access_key_id, secret_key, session_token = response.split(":")

        if self._s3_resource is None:
            self._s3_resource = boto3.resource(
                's3',
                aws_access_key_id=access_key_id,
                aws_secret_access_key=secret_key,
                aws_session_token=session_token,
                endpoint_url=os.environ["MINIO_ENDPOINT"], 
                config=Config(
                    signature_version=self._signature_version,
                    connect_timeout=6000,
                    read_timeout=6000,
                    retries={
                        'total_max_attempts':10,
                        'mode': 'standard'
                }),
                )

        s3_client = self._s3_resource.meta.client
        return s3_client
