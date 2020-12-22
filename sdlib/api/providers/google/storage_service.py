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
import math
import os
import struct
import sys
import time

import crc32c
import requests
from sdlib.api.seismic_store_service import SeismicStoreService
from sdlib.api.storage_service import StorageFactory, StorageService
from six.moves import urllib
from tqdm import tqdm


@StorageFactory.register(provider="google")
class GoogleStorageService(StorageService):
    __STORAGE_CLASSES = ['REGIONAL', 'MULTI_REGIONAL', 'NEARLINE', 'COLDLINE']
    __STORAGE_LOCATION_MR = ['ASIA', 'EU', 'US']
    __STORAGE_EP = 'https://www.googleapis.com/storage/v1'
    __STORAGE_UPlOAD_EP = 'https://www.googleapis.com/upload/storage/v1'

    def __init__(self, auth):
        super(GoogleStorageService, self).__init__(auth=auth)
        self._seistore_svc = SeismicStoreService(auth=auth)
        self._chunkSize = 20 * 1048576

    def object_delete(self, objname, dataset):
        url = self.__STORAGE_EP \
              + '/b/' \
              + dataset.gcsurl.split("/")[0] \
              + "/o/" + dataset.gcsurl.split("/")[1] \
              + "%2F" \
              + urllib.parse.quote(objname, safe='')

        token = self._seistore_svc.get_storage_access_token(dataset.tenant,
                                                            dataset.subproject,
                                                            False)
        header = {
            'content-type': 'application/json',
            'Authorization': 'Bearer ' + token,
        }

        rx = requests.delete(url=url, headers=header)

        if rx.status_code != 204:
            raise Exception('[' + str(rx.status_code) + '] ' + rx.text)

    # to add an empty object / dummy object
    def object_add(self, objname, dataset):
        url = self.__STORAGE_UPlOAD_EP \
              + '/b/' \
              + dataset.gcsurl.split("/")[0] \
              + "/o?uploadType=media&name=" \
              + dataset.gcsurl.split("/")[1] \
              + "%2F" \
              + urllib.parse.quote(objname, safe='')

        token = self._seistore_svc.get_storage_access_token(dataset.tenant,
                                                            dataset.subproject,
                                                            False)
        header = {
            'content-type': 'application/json',
            'Authorization': 'Bearer ' + token,
        }

        rx = requests.post(url=url, headers=header)

        if rx.status_code != 200:
            raise Exception('[' + str(rx.status_code) + '] ' + rx.text)

    def object_upload(self, bucket, objname, data, tenant, subproject):
        url = self.__STORAGE_UPlOAD_EP \
              + '/b/' \
              + bucket \
              + "/o?uploadType=media&name=" \
              + urllib.parse.quote(objname, safe='')

        token = self._seistore_svc.get_storage_access_token(tenant,
                                                            subproject, False)
        header = {
            'content-type': 'application/octet-stream',
            'Authorization': 'Bearer ' + token,
        }

        rx = requests.post(url=url, headers=header, data=data)

        if rx.status_code != 200:
            raise Exception('[' + str(rx.status_code) + '] ' + rx.text)

    def upload_resumable_start(self, bucket, objname, dataset, totsize):
        url = self.__STORAGE_UPlOAD_EP \
              + '/b/' \
              + bucket \
              + "/o?uploadType=resumable&name=" \
              + urllib.parse.quote(objname, safe='')

        token = self._seistore_svc.get_storage_access_token(dataset.tenant,
                                                            dataset.subproject,
                                                            False)

        header = {
            'content-type': 'application/json',
            'Authorization': 'Bearer ' + token,
            'X-Upload-Content-Length': str(totsize),
            'User-Agent': 'sdutil'
        }

        rx = requests.post(url=url, headers=header)

        if rx.status_code != 200:
            raise Exception('[' + str(rx.status_code) + '] ' + rx.text)

        return rx.headers['Location']

    def upload_resumable_continue(self, location, bts, ssize, esize,
                                  totsize, tenant, subproject):
        token = self._seistore_svc.get_storage_access_token(tenant,
                                                            subproject, False)
        header = {
            'Authorization': 'Bearer ' + token,
            'Content-Length': str(len(bts)),
            'Content-Range': ('bytes ' + str(ssize) + '-' +
                              str(esize) + '/' + str(totsize))
        }

        rx = requests.put(url=location, data=bts, headers=header)

        if (rx.status_code != 200
                and rx.status_code != 308
                and rx.status_code != 503):
            raise Exception('[' + str(rx.status_code) + '] ' + rx.text)

        if rx.status_code == 503:
            token = self._seistore_svc.get_storage_access_token(tenant,
                                                                subproject,
                                                                False)
            header = {
                'Authorization': 'Bearer ' + token,
                'Content-Length': '0',
                'Content-Range': 'bytes */' + str(totsize),
                'User-Agent': 'sdutil'
            }

            rx = requests.put(url=location, headers=header)

            if rx.status_code != 200 and rx.status_code != 308:
                raise Exception('[' + str(rx.status_code) + '] ' + rx.text)

    def object_download(self, bucket, obj, tenant,
                        subproject, bfrom=None, bto=None):
        url = 'https://' \
              + bucket \
              + '.' \
              + 'storage.googleapis.com' \
              + '/' \
              + urllib.parse.quote(obj, safe='') \
              + '?alt=media'

        token = self._seistore_svc.get_storage_access_token(tenant,
                                                            subproject, True)
        header = {
            'content-type': 'application/octet-stream',
            'Authorization': 'Bearer ' + token,
        }

        if bfrom is not None and bto is not None:
            header['Range'] = 'bytes=' + str(bfrom) + '-' + str(bto)

        rx = requests.get(url=url, headers=header)

        if rx.status_code != 200 and rx.status_code != 206:
            raise Exception('[' + str(rx.status_code) + '] ' + rx.text)

        return rx.content

    def object_attribute(self, bucket, objname, attribute, tenant, subproject):
        url = self.__STORAGE_EP \
              + '/b/' \
              + bucket \
              + '/o/' \
              + urllib.parse.quote(objname, safe='') \
              + "?fields=" \
              + attribute

        token = self._seistore_svc.get_storage_access_token(tenant,
                                                            subproject, True)
        header = {
            'Authorization': 'Bearer ' + token,
        }

        rx = requests.get(url=url, headers=header)

        if rx.status_code != 200:
            raise Exception('[' + str(rx.status_code) + '] ' + rx.text)

        return rx.json()[attribute]

    def object_size(self, bucket, objname, tenant, subproject):
        return self.object_attribute(bucket, objname,
                                     'size', tenant, subproject)

    # Abstracted from Uploader
    def upload(self, filename, dataset):
        print('')
        print('- Initializing transfer session ... ', end='')
        fsize = os.path.getsize(filename)
        nread = int(fsize / self._chunkSize)
        rest = fsize - self._chunkSize * nread
        print('OK')
        bucket = dataset.gcsurl.split("/")[0]
        objname = dataset.gcsurl.split("/")[1] + "/0"
        print('- Initializing resumable-transfer location ... ', end='')
        sys.stdout.flush()
        location = self.upload_resumable_start(bucket, objname, dataset, fsize)
        print('OK')
        sys.stdout.flush()
        crc32c_local_digest = 0
        start_time = time.time()
        with open(filename, "rb") as fx:
            bts = 0

            bar='- Uploading Data [ {percentage:3.0f}%  |{bar}|  {n_fmt}/{total_fmt}  -  {elapsed}|{remaining}  -  {rate_fmt}{postfix} ]'
            with tqdm(total=fsize, bar_format=bar, unit='B', unit_scale=True, unit_divisor=1024) as pbar:
                for ii in range(0, nread):
                    bts = fx.read(self._chunkSize)
                    crc32c_local_digest = crc32c.crc32(bts, crc32c_local_digest)
                    self.upload_resumable_continue(
                        location, bts, ii * self._chunkSize,
                                        (ii + 1) * self._chunkSize - 1,
                        fsize, dataset.tenant,
                        dataset.subproject)
                    pbar.update(self._chunkSize)

                bts = fx.read(rest)
                crc32c_local_digest = crc32c.crc32(bts, crc32c_local_digest)
                self.upload_resumable_continue(
                    location, bts, nread *
                                    self._chunkSize,
                                    nread * self._chunkSize + rest - 1,
                    fsize, dataset.tenant, dataset.subproject)
                pbar.update(rest)

            crc32c_local_digest = base64.b64encode(struct.pack(">I", crc32c_local_digest)).decode("utf-8")    
            crc32c_remote = self.object_attribute(bucket, objname, 'crc32c', dataset.tenant, dataset.subproject)
            if crc32c_local_digest == crc32c_remote:
                ctime = time.time() - start_time + sys.float_info.epsilon
                print('- Transfer completed: ' +
                    str((fsize / 1048576.0) / ctime) + ' [MB/s]')
                sys.stdout.flush()
                return True
            else:
                print('- Transfer failed: crc32c mistmatch, please try again')
                return False

    # Abstracted from Downloader
    def download(self, localfilename, dataset):

        gcsurl = dataset.gcsurl.split("/")
        bucket = gcsurl[0]
        objname = gcsurl[1]

        print('')
        start_time = time.time()

        # download partial objects
        cursize = 0
        with open(localfilename, 'wb') as lfile:
            nobjects = dataset.filemetadata['nobjects']
            for obj in range(0, nobjects):
                cursize_incr, crc32c_local = self.downloadObject(lfile, bucket, objname + '/' +
                    str(obj), dataset, cursize)
                crc32c_remote = self.object_attribute(bucket, objname + '/' +
                    str(obj), 'crc32c', dataset.tenant, dataset.subproject) 
                crc32c_local = base64.b64encode(struct.pack(">I", crc32c_local)).decode("utf-8")  
                if crc32c_remote != crc32c_local:
                    lfile.close()
                    os.remove(localfilename)
                    print('- Transfer failed: crc32c mistmatch, please try again')
                    
                cursize =+ cursize_incr                                              

            lfile.close()
            ctime = time.time() - start_time + sys.float_info.epsilon
            speed = str(round(((dataset.filemetadata['size'] / 1048576.0) /
                               ctime), 3))
            print('- Transfer completed: ' + speed + ' [MB/s]')

        # download seismicmeta companion if present
        if dataset.seismicmeta is not None:
            with open(localfilename + '_seismicmeta.json', 'w') as outfile:
                json.dump(dataset.seismicmeta, outfile)
            outfile.close()

        return True

    # Abstracted from Downloader
    def downloadObject(self, lfile, bucket, obj, dataset, cursize):

        objsize = int(self.object_size(bucket, obj, dataset.tenant,
                                       dataset.subproject))
        ntrx = int(math.floor(objsize / self._chunkSize))
        rtrx_size = objsize - ntrx * self._chunkSize
        crc32c_local_digest = 0

        bar='- Downloading Data [ {percentage:3.0f}%  |{bar}|  {n_fmt}/{total_fmt}  -  {elapsed}|{remaining}  -  {rate_fmt}{postfix} ]'
        with tqdm(total=dataset.filemetadata['size'], bar_format=bar, unit='B', unit_scale=True, unit_divisor=1024) as pbar:
            for ii in range(0, ntrx):
                sstart = self._chunkSize * ii
                ssend = self._chunkSize * (ii + 1) - 1
                bts = self.object_download(bucket, obj, dataset.tenant,
                                           dataset.subproject, sstart, ssend)
                lfile.write(bts)
                cursize = cursize + self._chunkSize
                crc32c_local_digest = crc32c.crc32(bts, crc32c_local_digest)
                pbar.update(self._chunkSize)

            if rtrx_size != 0:
                sstart = self._chunkSize * ntrx
                ssend = self._chunkSize * ntrx + rtrx_size - 1
                bts = self.object_download(bucket, obj, dataset.tenant,
                                           dataset.subproject, sstart, ssend)
                lfile.write(bts)
                crc32c_local_digest = crc32c.crc32(bts, crc32c_local_digest)
                pbar.update(rtrx_size)

        return objsize, crc32c_local_digest

    @staticmethod
    def get_storage_regions():
        return ['ASIA', 'EU', 'US', 'NORTHAMERICA-NORTHEAST1', 'US-CENTRAL1', 'US-EAST1', 'US-EAST4', 'US-WEST1', 'SOUTHAMERICA-EAST1', 
                    'EUROPE-WEST1', 'EUROPE-WEST2', 'EUROPE-WEST3', 'EUROPE-WEST4', 'ASIA-EAST1', 'ASIA-NORTHEAST1', 'ASIA-SOUTH1', 
                    'ASIA-SOUTHEAST1', 'AUSTRALIA-SOUTHEAST1']

    @staticmethod
    def get_storage_classes():
        return GoogleStorageService.__STORAGE_CLASSES

    @staticmethod
    def get_storage_multi_regions():
        return GoogleStorageService.__STORAGE_LOCATION_MR
