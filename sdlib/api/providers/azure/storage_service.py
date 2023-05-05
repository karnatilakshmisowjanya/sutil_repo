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
import hashlib
import json
import os
import sys
import uuid

from alive_progress import alive_bar
from sdlib.api.seismic_store_service import SeismicStoreService
from sdlib.api.storage_service import StorageFactory, StorageService
from azure.storage.blob import ContainerClient, ContentSettings


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
        # Calculate the md5 checksum first
        file_md5_hash = hashlib.md5()
        # Calculate the checksum in chunks
        with open(filename, "rb") as f:
            for file_chunk in iter(lambda: f.read(32 * 1048576), b""):
                file_md5_hash.update(file_chunk)

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
                                bar(current / total)

                        file_md5_hash = file_md5_hash.hexdigest()
                        blob_client.upload_blob(lfile, validate_content=True,
                                                raw_response_hook=callback,
                                                content_settings=ContentSettings(
                                                    content_md5=bytearray.fromhex(file_md5_hash)
                                                ))
                        blob_properties = blob_client.get_blob_properties()
                        content_md5 = bytearray.hex(blob_properties.content_settings.get('content_md5'))
                        if content_md5 != file_md5_hash:
                            # delete the uploaded blob
                            blob_client.delete_blob()
                            raise Exception('Content md5 does not match for the uploaded blob')

            lfile.close()
            print('\nTransfer completed\n'
                  'File Checksum: ' + file_md5_hash + '\n' +
                  'Checksum matches!!!\n')
        return {"num_of_objects": 1, "md5_checksum": file_md5_hash}

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
            md5_final_hash = hashlib.md5()
            uploaded_blob_properties = None
            if totalFileSize > 0:
                with open(filename, "rb") as lfile:
                    block_id_lst = list()
                    with alive_bar(totalFileSize, manual=True, title="Uploading", theme='ascii') as bar:
                        while True:
                            with container_client.get_blob_client(str(block_count)) as blob_client:
                                chunk = lfile.read(chunk_size * 1048576)
                                totalBytesRead = lfile.tell()

                                if not chunk:
                                    if len(block_id_lst) > 0:
                                        blob_client.commit_block_list(block_id_lst)
                                        bar(totalBytesRead / totalFileSize)
                                    break
                                # calculate the md5 for the current chunk
                                current_chunk_md5 = hashlib.md5()
                                current_chunk_md5.update(chunk)
                                md5_ba = bytearray.fromhex(current_chunk_md5.hexdigest())

                                block_id = base64.b64encode(uuid.uuid4().hex.encode())
                                res = blob_client.stage_block(block_id,
                                                              chunk,
                                                              len(chunk),
                                                              validate_content=True)
                                # Compare the md5 of this chunk of local file to the one in response of stage block
                                if md5_ba != res['content_md5']:
                                    # Cleanup, existing partially created records
                                    block_count_to_delete = block_count
                                    while block_count_to_delete >= 0:
                                        with container_client.get_blob_client(
                                                str(block_count_to_delete)) as blob_client_for_deletion:
                                            blob_client_for_deletion.delete_blob()
                                        block_count_to_delete -= 1
                                    raise Exception('MD5 content mismatch, aborting')

                                # Continuously update the md5 in chunks, to get md5 of whole file
                                md5_final_hash.update(chunk)
                                block_id_lst.append(block_id)
                                if len(block_id_lst) >= max_allowed_uncommmited_blocks:
                                    # commit the block and set the md5 in content_settings
                                    blob_client.commit_block_list(block_id_lst,
                                                                  content_settings=ContentSettings(
                                                                      content_md5=bytearray.fromhex(
                                                                          md5_final_hash.hexdigest()
                                                                      )))
                                    bar(totalBytesRead / totalFileSize)
                                    block_count += 1
                                    block_id_lst = []

                                # Retrieve blob properties, for validation that the content-md5 is indeed reflecting
                                uploaded_blob_properties = blob_client.get_blob_properties()

                content_md5_of_uploaded_blob = bytearray.hex(
                    uploaded_blob_properties.content_settings.get('content_md5'))
                md5_final_hash = md5_final_hash.hexdigest()

                # Although I doubt, this will ever be the case
                if content_md5_of_uploaded_blob != md5_final_hash:
                    # Cleanup, existing partially created records
                    block_count_to_delete = block_count - 1  # block_count is incremented in the end of previous loop
                    while block_count_to_delete >= 0:
                        with container_client.get_blob_client(str(block_count_to_delete)) as blob_client:
                            # delete the partially created record
                            blob_client.delete_blob()
                            block_count_to_delete -= 1
                    raise Exception('Content md5 does not match for the uploaded blob')

                # Printing "checksum matches", since it's the only possible scenario here,
                # Otherwise we'd end up throwing exception and won't come here

                print('\nTransfer completed\n'
                      'File Checksum: ' + md5_final_hash + '\n' +
                      'Checksum matches!!!\n')
                return {"num_of_objects": block_count, "md5_checksum": md5_final_hash}
            else:
                raise Exception(filename + " is empty ")

    def download(self, localfilename, dataset):
        """Downloads dataset(blob) from azure storage container"""

        dataset_size = dataset.filemetadata["size"]
        sas_url = self._get_sas_url(dataset, False)
        counter = 0
        current_size = 0
        try:
            # md5 checksum for comparison
            blob_properties_file_checksum = None
            with alive_bar(dataset_size, manual=True, theme='ascii') as bar:
                with open(localfilename, 'wb') as lfile:
                    while current_size < dataset_size:
                        with ContainerClient.from_container_url(
                                container_url=sas_url,
                                max_block_size=self._maxBlockSize,
                                use_byte_buffer=True,
                                max_concurrency=self._max_concurrency,
                                max_single_put_size=self._max_single_put_size,
                                connection_timeout=100) as container_client:
                            with container_client.get_blob_client(str(counter)) as blob_client:
                                print("Downloading Chunk # " + str(counter + 1))
                                current_size = current_size + blob_client.download_blob(validate_content=True).readinto(
                                    lfile)

                                counter = counter + 1
                                bar(current_size / dataset_size)
                                print("Current: " + str(current_size) + " of " + str(dataset_size) + '\n')
                                # Get the file checksum
                                blob_properties_file_checksum = blob_client.get_blob_properties().content_settings.get(
                                    "content_md5", None)
            # only do checksum printing if its present in the source/blob file
            if blob_properties_file_checksum:
                # md5 checksum for comparison
                local_file_checksum = hashlib.md5()
                # get the md5 of downloaded file
                with open(localfilename, "rb") as lfile:
                    for file_chunk in iter(lambda: lfile.read(32 * 1048576), b""):
                        local_file_checksum.update(file_chunk)
                blob_properties_file_checksum = bytearray.hex(blob_properties_file_checksum)
                local_file_checksum = local_file_checksum.hexdigest()

                print("Source File Checksum: " + blob_properties_file_checksum + '\n' +
                      "Destination File Checksum: " + local_file_checksum)

                if local_file_checksum != blob_properties_file_checksum:
                    print('Checksum mismatch!!!')
                else:
                    print('Checksum matches!!!')

            print('\nTransfer completed')

        except Exception as e:
            print("Exception: " + str(e))

        lfile.close()

        if dataset.seismicmeta is not None:
            with open(localfilename + '_seismicmeta.json', 'w') as outfile:
                json.dump(dataset.seismicmeta, outfile)
            outfile.close()

        return True
