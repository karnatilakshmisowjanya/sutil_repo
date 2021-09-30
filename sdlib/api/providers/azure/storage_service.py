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

import os
import sys

from alive_progress import alive_bar
from sdlib.api.seismic_store_service import SeismicStoreService
from sdlib.api.storage_service import StorageFactory, StorageService
from six.moves import urllib
from tqdm import tqdm

from azure.storage.blob import ContainerClient

from ....shared.config import Config


@StorageFactory.register(provider="azure")
class AzureStorageService(StorageService):
    def __init__(self, auth):
        super(AzureStorageService, self).__init__(auth=auth)
        self._seistore_svc = SeismicStoreService(auth=auth)
        self._chunkSize = 64 * 1024 * 1024
        self._max_single_put_size = 64 * 1024 * 1024
        self._max_concurrency = 10

    def _get_sas_url(self, dataset, readonly):
        container_id = dataset.gcsurl.split("/")[0]
        dataset_id = dataset.gcsurl.split("/")[1]
        access_token = self._seistore_svc.get_storage_access_token(dataset.tenant, dataset.subproject, readonly)
        return access_token.replace(container_id, container_id + "/" + dataset_id)

    def upload(self, filename, dataset):
        """ Uploads dataset(blob) to azure storage container"""
        print('')
        sas_url = self._get_sas_url(dataset, False)
        dataset_id = dataset.gcsurl.split("/")[1]

        with open(filename, "rb") as lfile:
            print('- Initializing transfer session ... ', end='')
            sys.stdout.flush()
            with ContainerClient.from_container_url(container_url=sas_url,
                                                    max_block_size=self._chunkSize,
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
                        
                        blob_client.upload_blob(lfile, validate_content=False, 
                        raw_response_hook=callback)
                        
            lfile.close()
            print('Transfer completed')

        return True

    def upload_test(self, filename, dataset):
        sas_url = self._get_sas_url(dataset, False)

    def download(self, localfilename, dataset):
        """Downloads dataset(blob) from azure storage container"""
        print('Begin Download')
        gcsurl = dataset.gcsurl.split("/")
        dataset_id = gcsurl[1]
        dataset_size = dataset.filemetadata["size"]
        sas_url = self._get_sas_url(dataset, False)
        counter = 0
        current_size = 0
        try:
            with alive_bar(dataset_size, manual=True) as bar:
                with open(localfilename, 'wb') as lfile:
                    while (current_size < dataset_size):
                        with ContainerClient.from_container_url(
                                container_url=sas_url,
                                max_block_size=self._chunkSize,
                                use_byte_buffer=True,
                                max_concurrency=self._max_concurrency,
                                max_single_put_size=self._max_single_put_size, 
                                connection_timeout=100) as container_client:
                            with container_client.get_blob_client(str(counter)) as blob_client:
                                print("Downloading Chunk # " + str(counter + 1))
                                blob_client.download_blob(validate_content=True).readinto(lfile)
                                counter = counter + 1
                                current_size = os.fstat(lfile.fileno()).st_size
                                bar(current_size/dataset_size)
                                print("Current: " + str(current_size) + " of " + str(dataset_size))
        except:
            print("Finished Chunks")

        lfile.close()
        print('Transfer completed')

        if dataset.seismicmeta is not None:
            with open(localfilename + '_seismicmeta.json', 'w') as outfile:
                json.dump(dataset.seismicmeta, outfile)
            outfile.close()

        return True




