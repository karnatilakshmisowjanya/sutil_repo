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

from __future__ import print_function
import math
import sys
import time
import os
import boto3
from boto3.s3.transfer import S3Transfer, TransferConfig
from botocore.client import Config
import tqdm
from sdlib.api.dataset import Dataset
from sdlib.api.seismic_store_service import SeismicStoreService
from sdlib.api.storage_service import StorageFactory, StorageService

@StorageFactory.register(provider="aws")
class AwsStorageService(StorageService):
    __STORAGE_CLASSES = ['REGIONAL']
    _s3_client = None
    _s3_resource = None
    _signature_version = 's3v4'

    def __init__(self, auth):
        super().__init__(auth=auth)
        self._seistore_svc = SeismicStoreService(auth=auth)
        self.aws_bucketname_string_separator = '$$'
        self._chunkSize = 20 * 1048576

    def upload(self, file_name:str, dataset: Dataset, object_name=None):
        """Upload file to S3 bucket

        Args:
            file_name (str): the path to the local file
            dataset (str): the dataset where this file should be uploaded
            object_name (str, optional): S3 object key. Default is None.

        Returns:
            bool: did the upload succeed?
        """

        # for now AWS's gcsurl is "bucket_name$$subproject_folder/dataset_folder"
        bucket_name, s3_folder_name = dataset.gcsurl.split(self.aws_bucketname_string_separator)
        print(dataset.gcsurl)

        # If S3 object_name was not specified, use "0"
        if object_name is None:
            object_name = f"{s3_folder_name}/0"

        if self._s3_client is None:
            self._s3_client = self.get_s3_client(self, dataset)
        
        transfer_config = TransferConfig(multipart_threshold=9999999999999999, use_threads=True, max_concurrency=10)
        transfer = S3Transfer(client=self._s3_client, config=transfer_config)

        bar_format = '- Uploading Data [ {percentage:3.0f}%  |{bar}|  {n_fmt}/{total_fmt}  -  {elapsed}|{remaining}  -  {rate_fmt}{postfix} ]'
        
        # Upload the file
        with tqdm.tqdm(total=os.path.getsize(file_name), bar_format=bar_format, unit='B', unit_scale=True, unit_divisor=1024) as pbar:
            transfer.upload_file(file_name, bucket_name, object_name, callback=AwsStorageService._progress_hook(pbar))
        print("File [" + file_name + "] uploaded successfully")
        
        return True

    def download(self, local_filename:str, dataset: Dataset):
        """download object from S3

        Args:
            local_filename (str): what to name the downloaded file, including type (.ext)
            dataset (str): the dataset URL

        Raises:
            e: ClientError

        Returns:
            bool: did the download succeed?
        """

        bucket_name, s3_folder_name = dataset.gcsurl.split(self.aws_bucketname_string_separator)
        start_time = time.time()

        # download partial objects
        cursize = 0
        with open(local_filename, 'wb') as localFile:
            nobjects = dataset.filemetadata['nobjects']
            for obj in range(0, nobjects):
                object_name = f"{s3_folder_name}/" + str(obj)
                print(f"{object_name!r}")
                cursize_incr = self.downloadObject(localFile, bucket_name, object_name, dataset, cursize)
                cursize =+ cursize_incr
            ctime = time.time() - start_time + sys.float_info.epsilon
            speed = str(round(((dataset.filemetadata['size'] / 1048576.0) / ctime), 3))
            print('- Transfer completed: ' + speed + ' [MB/s]')
            
        return True

    def downloadObject(self, localFile, bucket, obj, dataset, cursize):
        """download an object from s3 ( one of many )

        Args:
            localFile (FileIO): a local file object
            bucket (str): the s3 bucket name
            obj (int): a number representing this objects index out of all the objects
            dataset (Dataset): a Dataset object, from sdlib.api.dataset
            cursize (int): the current size of the most recent object ( or the size of a stray dog... get it? )

        Returns:
            objsize: the size of the object
        """

        if self._s3_client is None:
            self._s3_client = self.get_s3_client(self, dataset)
    
        objsize = int(self._s3_resource.Object(bucket, obj).content_length)
        num_transfers = int(math.floor(objsize / self._chunkSize))
        remaining_transfer_size = objsize - num_transfers * self._chunkSize

        bar='- Downloading Data in Chunks [ {percentage:3.0f}%  |{bar}|  {n_fmt}/{total_fmt}  -  {elapsed}|{remaining}  -  {rate_fmt}{postfix} ]'
        # with tqdm.tqdm(total=dataset.filemetadata['size'], bar_format=bar, unit='B', unit_scale=True) as pbar:
        # TODO: provide progress bar based on bytes for download
        
        # With the upload, we provide a progress bar based on bytes.
        # With the download we provide a progress bar based on for loop iterations
        for ii in tqdm.tqdm(range(0, num_transfers), bar_format=bar, unit_scale=True):
            start_byte = self._chunkSize * ii
            stop_byte = self._chunkSize * (ii + 1) - 1
            # download next chunk of the object
            resp = self._s3_client.get_object(Bucket=bucket, Key=obj, Range='bytes={}-{}'.format(start_byte, stop_byte))
            for i in resp['Body']:
                localFile.write(i)

            cursize = cursize + self._chunkSize

        if remaining_transfer_size != 0:
            start_byte = self._chunkSize * num_transfers
            stop_byte = self._chunkSize * num_transfers + remaining_transfer_size - 1
            # download any remainder of the object smaller than standard chunksize
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
    def get_storage_regions():
        """return AWS regions

        Returns:
            list: applicable AWS regions
        """
        return AwsStorageService._get_regions()

    @staticmethod
    def get_storage_classes():
        """return storage classes

        Returns:
            list: storage classes
        """
        return AwsStorageService.__STORAGE_CLASSES

    @staticmethod
    def get_storage_multi_regions():
        """return regions available for multi-region deployment

        Returns:
            list: applicable regions
        """
        return AwsStorageService._get_regions()
    
    @staticmethod
    def _get_regions():
        """return simplistic regions. # TODO: do this dynamically

        Returns:
            list: applicable regions
        """
        return ["us-east-1", "US-CENTRAL1"]

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
