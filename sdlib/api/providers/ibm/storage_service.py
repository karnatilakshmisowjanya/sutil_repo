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
import math
import os
import sys
import time
import boto3
from boto3.s3.transfer import S3Transfer, TransferConfig
from botocore.client import Config
import tqdm
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
        self._chunkSize = 20 * 1048576

    def upload(self, file_name: str, dataset: Dataset, object_name=None):
        """Upload file to S3 bucket

               Args:
                   file_name (str): the path to the local file
                   dataset (str): the dataset where this file should be uploaded
                   object_name (str, optional): S3 object key. Default is None.

               Returns:
                   bool: did the upload succeed?
               """

        bucket_name, s3_folder_name = dataset.gcsurl.split('/')
        object_name = f"{s3_folder_name}/" + "0"

        if self._s3_client is None:
            self._s3_client = self.get_s3_client(self, dataset)
        transfer_config = TransferConfig(multipart_threshold=9999999999999999, use_threads=True, max_concurrency=10)
        transfer = S3Transfer(client=self._s3_client, config=transfer_config)

        bar_format = '- Uploading Data [ {percentage:3.0f}%  |{bar}|  {n_fmt}/{total_fmt}  -  {elapsed}|{remaining}  -  {rate_fmt}{postfix} ]'
        with tqdm.tqdm(
            total=os.path.getsize(file_name), bar_format=bar_format, 
            unit='B', unit_scale=True, unit_divisor=1024) as pbar:
                transfer.upload_file(filename=file_name, bucket=bucket_name, key=object_name, callback=IbmStorageService._progress_hook(pbar))
        print("File [" + file_name + "] uploaded successfully")

        self._seistore_svc._auth.refresh()
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
        start_time = time.time()

        # download partial objects
        cursize = 0
        with open(local_filename, 'wb') as localFile:
            nobjects = dataset.filemetadata['nobjects']
            for obj in range(0, nobjects):
                object_name = f"{s3_folder_name}/" + str(obj)
                cursize_incr = self.downloadObject(localFile, bucket_name, object_name, dataset, cursize)
                cursize =+ cursize_incr
            ctime = time.time() - start_time + sys.float_info.epsilon
            speed = str(round(((dataset.filemetadata['size'] / 1048576.0) / ctime), 3))
            print('- Transfer completed: ' + speed + ' [MB/s]')

        return True

    def downloadObject(self, localFile, bucket, obj, dataset, cursize):

        if self._s3_client is None:
            self._s3_client = self.get_s3_client(self, dataset)
    
        objsize = int(self._s3_resource.Object(bucket, obj).content_length)
        ntrx = int(math.floor(objsize / self._chunkSize))
        rtrx_size = objsize - ntrx * self._chunkSize

        # bar='- Downloading Data [ {percentage:3.0f}%  |{bar}|  {n_fmt}/{total_fmt}  -  {elapsed}|{remaining}  -  {rate_fmt}{postfix} ]'
        # with tqdm(total=dataset.filemetadata['size'], bar_format=bar, unit='B', unit_scale=True, unit_divisor=1024) as pbar:
        for ii in range(0, ntrx):
            start_byte = self._chunkSize * ii
            stop_byte = self._chunkSize * (ii + 1) - 1
            resp = self._s3_client.get_object(Bucket=bucket, Key=obj, Range='bytes={}-{}'.format(start_byte, stop_byte))
            for i in resp['Body']:
                localFile.write(i)

            cursize = cursize + self._chunkSize

        if rtrx_size != 0:
            start_byte = self._chunkSize * ntrx
            stop_byte = self._chunkSize * ntrx + rtrx_size - 1
            resp = self._s3_client.get_object(Bucket=bucket, Key=obj, Range='bytes={}-{}'.format(start_byte, stop_byte))
            for i in resp['Body']:
                localFile.write(i)

        return objsize

    
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

        response = self._seistore_svc.get_storage_access_token(
            tenant=dataset.tenant, subproject=dataset.subproject,readonly=False)

        access_key_id, secret_key, session_token = response.split(":")

        if self._s3_resource is None:
            self._s3_resource = boto3.resource(
                's3',
                endpoint_url=self._endpointURL,
                aws_access_key_id=access_key_id,
                aws_secret_access_key=secret_key,
                aws_session_token=session_token,
                config=Config(
                signature_version=self._signature_version,
                connect_timeout=6000,
                read_timeout=6000,
                retries={
                    'total_max_attempts':10,
                    'mode': 'standard'
                }),
                region_name=self._region)

        s3_client = self._s3_resource.meta.client
        return s3_client
