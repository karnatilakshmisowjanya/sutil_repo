# -*- coding: utf-8 -*-
# Copyright 2017-2024, Schlumberger
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
from datetime import datetime
import hashlib
import json
import os
import re
import sys
import uuid
import time

from alive_progress import alive_bar
from sdlib.api.seismic_store_service import SeismicStoreService
from sdlib.api.storage_service import StorageFactory, StorageService
from azure.storage.blob import ContainerClient, ContentSettings


@StorageFactory.register(provider="azure")
class AzureStorageService(StorageService):
    def __init__(self, auth):
        super(AzureStorageService, self).__init__(auth=auth)
        self._seistore_svc = SeismicStoreService(auth=auth)
        self._max_block_size = 64 * 1024 * 1024
        self._max_single_put_size = 64 * 1024 * 1024
        self._max_single_get_size = 32 * 1024 * 1024
        self._max_concurrency = 10
        self._max_download_retries = 20
        self._max_download_retries_total = 50

    def _get_sas_url(self, dataset, readonly):
        if(dataset.access_policy != 'dataset'):
            access_token = self._seistore_svc.get_storage_access_token(
                tenant=dataset.tenant, subproject=dataset.subproject, readonly=readonly)
            container_id = dataset.gcsurl.split("/")[0]
            dataset_id = dataset.gcsurl.split("/")[1]
            return access_token.replace(container_id, container_id + "/" + dataset_id)
        else:
            return self._seistore_svc.get_storage_access_token(
                tenant=dataset.tenant,
                subproject=dataset.subproject,
                path=dataset.path,
                name=dataset.name,
                readonly=readonly)

    def upload(self, filename, dataset, **kwargs):
        '''
            **kwargs: chunk_size is in MiB
        '''
        chunk_size = int(kwargs.get('chunk_size', 32))
        storage_tier = (kwargs.get('storage_tier'))
        if chunk_size == 0:
            return self.upload_single_object(filename, dataset, storage_tier)
        else:
            return self.upload_multi_object(filename, dataset, storage_tier, chunk_size)

    def upload_single_object(self, filename, dataset, storage_tier):
        """ Uploads dataset(blob) to azure storage container"""
        print('')

        sas_url = self._get_sas_url(dataset, False)
        # Calculate the md5 checksum first
        file_md5_hash = hashlib.md5()
        # Calculate the checksum in chunks
        with open(filename, "rb") as f:
            for file_chunk in iter(lambda: f.read(32 * 1048576), b""):
                file_md5_hash.update(file_chunk)

        with open(filename, "rb") as local_file:
            print('- Initializing transfer session ... ', end='')
            sys.stdout.flush()
            with ContainerClient.from_container_url(container_url=sas_url,
                                                    max_block_size=self._max_block_size,
                                                    use_byte_buffer=True,
                                                    max_concurrency=self._max_concurrency,
                                                    max_single_put_size=self._max_single_put_size,
                                                    connection_timeout=100) as container_client:
                with container_client.get_blob_client("0") as blob_client:
                    file_size = os.path.getsize(filename)
                    with alive_bar(file_size, manual=True, title="Uploading") as bar:
                        def callback(response):
                            current = response.context['upload_stream_current']

                            if current is not None:
                                total = response.context["data_stream_total"]
                                bar(current / total)

                        file_md5_hash = file_md5_hash.hexdigest()
                        blob_client.upload_blob(local_file, validate_content=True,
                                                raw_response_hook=callback,
                                                content_settings=ContentSettings(
                                                    content_md5=bytearray.fromhex(file_md5_hash)
                                                ),
                                                standard_blob_tier=storage_tier)
                        blob_properties = blob_client.get_blob_properties()
                        # Retrieve blob storage tier from blob properties
                        blob_tier = str(blob_properties.blob_tier)
                        content_md5 = bytearray.hex(blob_properties.content_settings.get('content_md5'))
                        if content_md5 != file_md5_hash:
                            # delete the uploaded blob
                            blob_client.delete_blob()
                            raise Exception('Content md5 does not match for the uploaded blob')

            local_file.close()
            print('\nTransfer completed\n'
                  'File Checksum: ' + file_md5_hash + '\n' +
                  'Checksum matches!!!\n')
        return {"num_of_objects": 1, "md5_checksum": file_md5_hash, "blob_tier": blob_tier}

    def upload_multi_object(self, filename, dataset, storage_tier, chunk_size):
        """ Uploads dataset(blob) to azure storage container
            param: chunk size is in MiB
        """

        sas_url = self._get_sas_url(dataset, False)
        max_allowed_uncommitted_blocks = 1
        block_count = 0
        with ContainerClient.from_container_url(container_url=sas_url,
                                                use_byte_buffer=True,
                                                max_concurrency=self._max_concurrency,
                                                connection_timeout=100) as container_client:
            totalFileSize = os.path.getsize(filename)
            totalBytesRead = 0
            md5_final_hash = hashlib.md5()
            uploaded_blob_properties = None
            blob_tier = None
            if totalFileSize > 0:
                with open(filename, "rb") as local_file:
                    block_id_lst = list()
                    with alive_bar(totalFileSize, manual=True, title="Uploading", theme='smooth') as bar:
                        while True:
                            with container_client.get_blob_client(str(block_count)) as blob_client:
                                chunk = local_file.read(chunk_size * 1048576)
                                totalBytesRead = local_file.tell()

                                if not chunk:
                                    if len(block_id_lst) > 0:
                                        blob_client.commit_block_list(block_id_lst, standard_blob_tier=storage_tier)
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
                                if len(block_id_lst) >= max_allowed_uncommitted_blocks:
                                    # commit the block and set the md5 in content_settings
                                    blob_client.commit_block_list(block_id_lst,
                                                                  content_settings=ContentSettings(
                                                                      content_md5=bytearray.fromhex(
                                                                          md5_final_hash.hexdigest()
                                                                      )),
                                                                      standard_blob_tier=storage_tier)
                                    bar(totalBytesRead / totalFileSize)
                                    block_count += 1
                                    block_id_lst = []

                                # Retrieve blob properties, for validation that the content-md5 is indeed reflecting
                                uploaded_blob_properties = blob_client.get_blob_properties()

                                # Retrieve blob storage tier from blob properties
                                blob_tier = str(uploaded_blob_properties.blob_tier)

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
                return {"num_of_objects": block_count, "md5_checksum": md5_final_hash, "blob_tier": blob_tier }
            else:
                raise Exception(filename + " is empty ")

    def download(self, local_filename, dataset):
        """Downloads dataset(blob) from azure storage container"""

        dataset_size = dataset.filemetadata["size"]
        sas_url = self._get_sas_url(dataset, True)
        counter = 0
        current_size = 0
        size_array = []
        md5_array = []
        total_retries = 0
        print('')
        try:
            # md5 checksum for comparison
            blob_properties_file_checksum = None
            with alive_bar(dataset_size, manual=True, theme='smooth') as bar:
                with open(local_filename, 'wb') as local_file:
                    while current_size < dataset_size:
                        with ContainerClient.from_container_url(
                                container_url=sas_url,
                                use_byte_buffer=True,
                                max_concurrency=self._max_concurrency,
                                max_single_get_size=self._max_single_get_size,
                                connection_timeout=100) as container_client:
                            with container_client.get_blob_client(str(counter)) as blob_client:
                                retries = 0
                                while retries < self._max_download_retries:
                                    try:
                                        print('--------------------------------')
                                        print(f'Downloading Chunk # {counter + 1}, Attempt # {retries + 1}')
                                        print(f'Total downloaded size {current_size}, total written size: {local_file.tell()} (size-check: {current_size==local_file.tell()})')
                                        bytes_expected = blob_client.get_blob_properties().size
                                        bytes_read = blob_client.download_blob(validate_content=True).readinto(local_file)
                                        current_size = current_size + bytes_read
                                        size_array.append(bytes_read)
                                        print(f'Expected to read {bytes_expected}, actually read {bytes_read} (read-check: {bytes_expected == bytes_read})')

                                        counter = counter + 1
                                        print(f'Downloaded {current_size} of {dataset_size} (bytes)')
                                        # Get the file checksum
                                        blob_properties_file_checksum = blob_client.get_blob_properties().content_settings.get(
                                            "content_md5", None)
                                        md5_array.append(bytearray.hex(blob_client.get_blob_properties().content_settings.get(
                                            "content_md5", None)))
                                        if blob_properties_file_checksum:
                                            print(f'Chunk checksum {bytearray.hex(blob_properties_file_checksum)}')
                                        bar(current_size / dataset_size)                                        
                                        break
                                    except Exception as ex:
                                        retries = retries + 1
                                        total_retries = total_retries + 1
                                        print(f'Exception {ex} while download chunk #{counter + 1}')
                                        if total_retries > self._max_download_retries_total:
                                            raise ex
                                        else:
                                            if current_size != local_file.tell():
                                                print(f'Current size {current_size} does not match the stream size {local_file.tell()}')
                                                local_file.seek(current_size, os.SEEK_SET)
                                            print("Pausing before retry ...")
                                            time.sleep(10 + 5*retries)
            md5_array = tuple(md5_array)
            enable_md5_check = True
            # determine the blob size
            blob_size = 32 * 1048576
            if len(size_array) > 1:
                blob_size = size_array[0]
            # only do checksum printing if its present in the source/blob file
            if blob_properties_file_checksum:
                # md5 checksum for comparison
                local_file_checksum = hashlib.md5()
                # get the md5 of downloaded file
                with open(local_filename, "rb") as local_file:
                    for file_chunk in iter(lambda: local_file.read(blob_size), b""):
                        local_file_checksum.update(file_chunk)
                        if local_file_checksum.hexdigest() not in md5_array:
                            enable_md5_check = False
                            break
                blob_properties_file_checksum = bytearray.hex(blob_properties_file_checksum)
                local_file_checksum = local_file_checksum.hexdigest()

                print("Source File Checksum: " + blob_properties_file_checksum + '\n' +
                      "Destination File Checksum: " + local_file_checksum)
                if enable_md5_check:
                    if local_file_checksum != blob_properties_file_checksum:
                        print('Checksum mismatch!!!')
                    else:
                        print('Checksum matches!!!')
                else:
                    print('Warning: Checksum Skipped!')
            print('\nTransfer completed')

        except Exception as e:
            print("Exception: " + str(e))

        return True
    
    def download_object(self, connection_string, local_path=None, latest=False):
        # '''Download analytics reports'''
        # '''
    
        pos = connection_string.find('/', connection_string.find('://') + 3)
        base_url = connection_string[:pos]
        query_string = connection_string[pos + 1:]
        target = query_string.split('?')[0]
        rest = ''.join(query_string.split('?')[1:])
        parts = target.split('/');
        container_name = parts[0]
        prefix = '/'.join(parts[1:])
        cs = f"{base_url}/{container_name}?{rest}"

        try:
            with ContainerClient.from_container_url(
                    container_url=cs,
                    use_byte_buffer=True,
                    max_concurrency=self._max_concurrency,
                    max_single_put_size=self._max_single_put_size,
                    connection_timeout=100) as container_client:

                blob_list = container_client.list_blobs(name_starts_with=f"{prefix}/")
                base_path = os.path.join(
                    os.path.expanduser('~'), os.getcwd(), local_path) if local_path is not None else os.path.join(
                        os.path.expanduser('~'), os.getcwd())
                if latest:
                    # find the latest blob list
                    def extract_date(reports):
                        match = re.search(r'(\d{4})/(\d{2})/(\d{2})', reports)
                        if match:
                            return datetime.strptime(match.group(0), "%Y/%m/%d")
                        return None
                    # Extract dates and find the latest one
                    dates = [(blob, extract_date(blob.name)) for blob in blob_list]
                    latest_report = max(dates, key=lambda x: x[1] if x[1] else datetime.min)
                    # Display the latest report filename
                    print(f"The latest report is: {latest_report[0].name}\n")
                    blob_list = [latest_report[0]]

                for blob in blob_list:
                    file_name = (blob.name).replace('/', '-')
                    full_path = os.path.join(base_path, file_name)
                    try:
                        with open(full_path, 'wb') as lfile:
                            print(f"downloading report {file_name}...")
                            blob_client = container_client.get_blob_client(blob)
                            blob_data = blob_client.download_blob().readinto(lfile)
                    except Exception:
                        raise Exception(f"Invalid Argument: The specified output path \"{local_path}\" does not exist or is not a regular directory.")
                        

            print('\nDownload completed')

        except Exception as e:
            print(str(e))
