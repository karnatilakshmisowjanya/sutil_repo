# Copyright 2021 IBM Corp. All Rights Reserved.
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
from boto3.s3.transfer import S3Transfer
from botocore.client import Config
import tqdm
from botocore.exceptions import ClientError
from sdlib.api.dataset import Dataset
from sdlib.api.storage_service import StorageFactory, StorageService
from sdlib.api.seismic_store_service import SeismicStoreService


@StorageFactory.register(provider="ibm")
class IbmStorageService(StorageService):
    _endpointURL = None
    _region = None
    _signature_version = 's3v4'

    _s3_resource = None
    _s3_client = None
    _seistore_svc = None

    def __init__(self, auth, *args, **kwargs):
        super().__init__(auth, *args, **kwargs)
        self._seistore_svc = SeismicStoreService(auth=auth)
        self._endpointURL = os.getenv("COS_URL", "NA")
        self._region = os.getenv("COS_REGION", "NA")

    def upload(self, file_name: str, dataset: Dataset, object_name=None):
        """Upload file to S3 bucket

        Args:
            file_name (str): the path to the local file
            dataset (str): the dataset where this file should be uploaded
            object_name (str, optional): S3 object key. Default is None.

        Returns:
            bool: did the upload succeed?
        """

        # for now IBM's gcsurl is "bucket_name$$subproject_folder/dataset_folder"
        bucket_name, s3_folder_name = dataset.gcsurl.split('/')
        print(dataset.gcsurl)

        # If S3 object_name was not specified, use file_name
        if object_name is None:
            object_name = f"{s3_folder_name}/{dataset.name}"

        if self._s3_client is None:
            self._s3_client = self.get_s3_client(self, dataset)

        try:
            self._s3_client.create_bucket(Bucket=bucket_name, )
        except ClientError as err:
            print(err)

        transfer = S3Transfer(self._s3_client)

        bar_format = '- Uploading Data [ {percentage:3.0f}%  |{bar}|  {n_fmt}/{total_fmt}  -  {elapsed}|{remaining}  -  {rate_fmt}{postfix} ]'

        # Upload the file
        with tqdm.tqdm(total=os.path.getsize(file_name), bar_format=bar_format, unit='B', unit_scale=True,
                       unit_divisor=1024) as pbar:
            transfer.upload_file(file_name, bucket_name, object_name, callback=IbmStorageService._progress_hook(pbar))

        return True

    def download(self, local_filename: str, dataset: Dataset):
        """download object from S3

        Args:
            local_filename (str): what to name the downloaded file, including type (.ext)
            dataset (str): the dataset URL

        Raises:
            e: ClientError

        Returns:
            bool: did the download succeed?
        """

        bucket_name, s3_folder_name = dataset.gcsurl.split('/')
        # parse object name from the URL
        object_name = f"{s3_folder_name}/{dataset.name}"

        # get object's size from attr
        object_size = dataset.filemetadata['size']
        # create tqdm progress bar template
        bar_format = '- Downloading Data [ {percentage:3.0f}%  |{bar}|  {n_fmt}/{total_fmt}  -  {elapsed}|{remaining}  -  {rate_fmt}{postfix} ]'

        if self._s3_client is None:
            self._s3_client = self.get_s3_client(self, dataset)

        transfer = S3Transfer(self._s3_client)

        # Download the file
        with tqdm.tqdm(total=object_size, bar_format=bar_format, unit='B', unit_scale=True, unit_divisor=1024) as pbar:
            transfer.download_file(bucket_name, object_name, local_filename,
                                   callback=IbmStorageService._progress_hook(pbar))

        return True

    @staticmethod
    def _progress_hook(tqdm_instance):
        """update tqdm progress bar

        Args:
            t (tqdm.tqdm): instance of tqdm
        """

        def inner(bytes_amount):
            tqdm_instance.update(bytes_amount)

        return inner

    @staticmethod
    def get_s3_client(self, dataset):
        print("IBMBlobStorageFactory().get_s3_client")
        response = self._seistore_svc.get_storage_access_token(tenant=dataset.tenant, subproject=dataset.subproject,
                                                               readonly=False)
        # the response will be "acess_key_id:secret_key:session_token", so we parse it
        access_key_id, secret_key, session_token = response.split(":")

        if self._s3_resource is None:
            print("IBMBlobStorageFactory()._s3_resource is None")
            _s3_resource = boto3.resource('s3',
                                          endpoint_url=self._endpointURL,
                                          aws_access_key_id=access_key_id,
                                          aws_secret_access_key=secret_key,
                                          aws_session_token=session_token,
                                          config=Config(signature_version=self._signature_version),
                                          region_name=self._region)
            print("IBMBlobStorageFactory()._s3_resource: ", _s3_resource)

        s3_client = _s3_resource.meta.client
        print("IBMBlobStorageFactory().s3_client: ", s3_client)
        return s3_client
