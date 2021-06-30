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

from azure.storage.blob import ContainerClient
from lxml import html
from six.moves import urllib
from tqdm import tqdm

from sdlib.api.seismic_store_service import SeismicStoreService
from sdlib.api.storage_service import StorageFactory, StorageService

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
                                                    max_single_put_size=self._max_single_put_size) as container_client:
                with container_client.get_blob_client("0") as blob_client:
                    bar='- Uploading Data [ {percentage:3.0f}%  |{bar}|  {n_fmt}/{total_fmt}  -  {elapsed}|{remaining}  -  {rate_fmt}{postfix} ]'
                    with tqdm(total=os.path.getsize(filename), bar_format=bar, unit='B', unit_scale=True, unit_divisor=1024) as pbar:
                        def callback(response):
                            current = response.context['upload_stream_current']
                            if current is not None:
                                pbar.update(current)

                        blob_client.upload_blob(lfile, validate_content=True, raw_response_hook=callback)
            lfile.close()                                                
            print('- Transfer completed')

        return True

    def download(self, localfilename, dataset):
        """Downloads dataset(blob) from azure storage container"""
        print('')
        gcsurl = dataset.gcsurl.split("/")
        dataset_id = gcsurl[1]
        blob_size = dataset.filemetadata["size"]
        sas_url = self._get_sas_url(dataset, False)
        counter = 0
        current_size = 0
        try:
            with open(localfilename, 'wb') as lfile:
                while(current_size < blob_size):
                    with ContainerClient.from_container_url(container_url=sas_url) as container_client:
                        with container_client.get_blob_client(str(counter)) as blob_client:
                            bar='- Downloading Chunk Data [ {percentage:3.0f}%  |{bar}|  {n_fmt}/{total_fmt}  -  {elapsed}|{remaining}  -  {rate_fmt}{postfix} ]'
                            with tqdm(total=blob_size, bar_format=bar, unit='B', unit_scale=True, unit_divisor=1024) as pbar:
                                def callback(response):
                                    current = response.context['download_stream_current']
                                    if current is not None:
                                        pbar.update(current)

                            blob_client.download_blob(max_concurrency=blob_size,
                                                validate_content=True,raw_response_hook=callback).readinto(lfile)
                            counter=counter+1
                            current_size = os.fstat(lfile.fileno()).st_size
        except:                   
            print("Finished Chunks")
            
        lfile.close()
        print('- Transfer completed')

        if dataset.seismicmeta is not None:
            with open(localfilename + '_seismicmeta.json', 'w') as outfile:
                json.dump(dataset.seismicmeta, outfile)
            outfile.close()

        return True
