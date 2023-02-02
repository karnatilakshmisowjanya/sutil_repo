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

from __future__ import print_function

import base64
import json
import os
import sys
import time
import uuid

from alive_progress import alive_bar
from sdlib.api.seismic_store_service import SeismicStoreService
from sdlib.api.storage_service import StorageFactory, StorageService

from azure.core import MatchConditions
from azure.storage.blob import ContainerClient


@StorageFactory.register(provider="azure")
class AzureStorageService(StorageService):
    def __init__(self, auth):
        super(AzureStorageService, self).__init__(auth=auth)
        self._seistore_svc = SeismicStoreService(auth=auth)
        self._maxBlockSize = 64 * 1024 * 1024
        self._max_single_put_size = 64 * 1024 * 1024
        self._max_concurrency = 10

    def _get_sas_url(self, dataset, readonly):
        container_id = dataset.gcsurl.split("/")[0]
        dataset_id = dataset.gcsurl.split("/")[1]
        access_token = self._seistore_svc.get_storage_access_token(dataset.tenant, dataset.subproject, readonly)
        return access_token.replace(container_id, container_id + "/" + dataset_id)

    def upload(self, filename, dataset, **kwargs):
        '''
            **kwargs: chunk_size is in MiB
        '''
        chunk_size = int(kwargs.get('chunk_size', 32))
        if chunk_size == 0:
            return self.upload_single_object(filename, dataset)
        else:
            return self.upload_multi_object(filename, dataset, chunk_size)

    def upload_single_object(self, filename, dataset):
        """ Uploads dataset(blob) to azure storage container"""
        print('')

        sas_url = self._get_sas_url(dataset, False)

        with open(filename, "rb") as lfile:
            print('- Initializing transfer session ... ', end='')
            sys.stdout.flush()
            with ContainerClient.from_container_url(container_url=sas_url,
                                                    max_block_size=self._maxBlockSize,
                                                    use_byte_buffer=True,
                                                    max_concurrency=self._max_concurrency,
                                                    max_single_put_size=self._max_single_put_size,
                                                    connection_timeout=100) as container_client:
                with container_client.get_blob_client("0") as blob_client:
                    fsize = os.path.getsize(filename)
                    with alive_bar(fsize, manual=True, title="Uploading") as bar:
                        def callback(response):
                            current = response.context['upload_stream_current']

                            if current is not None:
                                total = response.context["data_stream_total"]
                                bar(current/total)

                        blob_client.upload_blob(lfile, validate_content=True,
                                                raw_response_hook=callback)

            lfile.close()
            print('\nTransfer completed ')

        return {"num_of_objects": 1}

    def upload_multi_object(self, filename, dataset, chunk_size):
        """ Uploads dataset(blob) to azure storage container
            param: chunksize is in MiB
        """

        sas_url = self._get_sas_url(dataset, False)
        max_allowed_uncommmited_blocks = 1
        block_count = 0
        with ContainerClient.from_container_url(container_url=sas_url,
                                                use_byte_buffer=True,
                                                max_concurrency=self._max_concurrency,
                                                connection_timeout=100) as container_client:
            totalFileSize = os.path.getsize(filename)
            totalBytesRead = 0
            if(totalFileSize > 0):
                with open(filename, "rb") as lfile:
                    block_id_lst = list()
                    with alive_bar(totalFileSize, manual=True, title="Uploading", theme='ascii') as bar:
                        while True:
                            with container_client.get_blob_client(str(block_count)) as blob_client:
                                chunk = lfile.read(chunk_size*1048576)
                                totalBytesRead = lfile.tell()

                                if not chunk:
                                    if(len(block_id_lst) > 0):
                                        blob_client.commit_block_list(block_id_lst)
                                        bar(totalBytesRead/totalFileSize)
                                    break

                                block_id = base64.b64encode(uuid.uuid4().hex.encode())
                                blob_client.stage_block(block_id, chunk, len(chunk), validate_content=True)
                                block_id_lst.append(block_id)

                                if len(block_id_lst) >= max_allowed_uncommmited_blocks:
                                    blob_client.commit_block_list(block_id_lst)
                                    bar(totalBytesRead/totalFileSize)
                                    block_count += 1
                                    block_id_lst = []
                print('\nTransfer completed ')
                return {"num_of_objects": block_count}
            else:
                raise Exception(filename + " is empty ")

    def download(self, localfilename, dataset):
        """Downloads dataset(blob) from azure storage container"""

        dataset_size = dataset.filemetadata["size"]
        sas_url = self._get_sas_url(dataset, False)
        counter = 0
        current_size = 0
        try:
            with alive_bar(dataset_size, manual=True, theme='ascii') as bar:
                with open(localfilename, 'wb') as lfile:
                    while (current_size < dataset_size):
                        with ContainerClient.from_container_url(
                                container_url=sas_url,
                                max_block_size=self._maxBlockSize,
                                use_byte_buffer=True,
                                max_concurrency=self._max_concurrency,
                                max_single_put_size=self._max_single_put_size,
                                connection_timeout=100) as container_client:
                            with container_client.get_blob_client(str(counter)) as blob_client:
                                print("Downloading Chunk # " + str(counter + 1))
                                current_size = current_size + blob_client.download_blob(validate_content=True).readinto(lfile)
                                counter = counter + 1
                                bar(current_size/dataset_size)
                                print("Current: " + str(current_size) + " of " + str(dataset_size))
            print('\nTransfer completed')
        except Exception as e:
            print("Exception: " + str(e))

        lfile.close()

        if dataset.seismicmeta is not None:
            with open(localfilename + '_seismicmeta.json', 'w') as outfile:
                json.dump(dataset.seismicmeta, outfile)
            outfile.close()

        return True
