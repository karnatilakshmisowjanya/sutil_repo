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

import json
import os
import sys

from sdlib.api.dataset import Dataset
from sdlib.api.seismic_store_service import SeismicStoreService
from sdlib.api.storage_service import StorageFactory
from sdlib.cmd.cmd import SDUtilCMD
from sdlib.cmd.helper import CMDHelper
from sdlib.shared.config import Config
from sdlib.shared.utils import Utils
from sdlib.shared.sdpath import SDPath
from sdlib.shared.storagetier import Tier


class Cp(SDUtilCMD):
    def __init__(self, auth):
        self._auth = auth

    @staticmethod
    def help():
        reg = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           'reg.json')
        CMDHelper.cmd_help(reg)

    def execute(self, args, keyword_args):

        if len(args) < 2:
            self.help()

        if Utils.isSDPath(args[0]) and Utils.isSDPath(args[1]):
            self.cp_sd_to_sd(args, keyword_args)
        elif Utils.isSDPath(args[0]):
            self.cp_sd_to_local(args, keyword_args)
        elif Utils.isSDPath(args[-1]) or Utils.isSDPath(args[-2]):
            self.cp_local_to_sd(args, keyword_args)
        else:
            raise Exception(
                '\n' +
                'Wrong Command: No seismic store dataset path has been '
                'specified or the provided one does not start with sd://.\n'
                '               For more information type "python sdutil cp"'
                ' to open the command help menu.')

    def cp_sd_to_sd(self, args, keyword_args):
        """ Copy a file from seismic_store to seismic_store
        """
        sdpath_from = str(args[0])
        sdpath_to = str(args[1])

        if Utils.isDatasetPath(sdpath_from) is False:
            raise Exception(
                '\n' + 'Wrong Command: ' + sdpath_from +
                ' is not a valid seismic store dataset path.\n'
                '               A valid seismic store dataset path must be in '
                'this form '
                'sd://<tenant_name>/<subproject_name>/<path>*/<dataset_name>.'
                '\n               For more information type "python sdutil cp"'
                ' to open the command help menu.')

        if Utils.isDatasetPath(sdpath_to) is False:
            raise Exception(
                '\n' + 'Wrong Command: ' + sdpath_to +
                ' is not a valid seismic store dataset path.\n' +
                '               A valid seismic store dataset path'
                ' must be in this form '
                'sd://<tenant_name>/<subproject_name>/<path>*/<dataset_name>.'
                '\n               For more information type "python sdutil cp"'
                ' to open the command help menu.')

        print('')

        SeismicStoreService(self._auth).dataset_cp(sdpath_from, sdpath_to)

        sys.stdout.flush()

    def cp_sd_to_local(self, args, keyword_args):
        """ Copy a seismic store file to local
        """
        if (os.name == "nt"):
            print('\nPlease consider wrapping sdutil path and local file between quotes, some examples:'
                  ' cp "sd://tenant/subproject/folder/dataset" "c:\\\\Users\\\\MyUser\\\\Desktop\\\\file"'
                  ' cp "sd://tenant/subproject/folder/dataset" "file"')
        sdpath = str(args[0])
        local_file = str(args[1])
        if ("--idtoken" in local_file):
            raise Exception(
                '\n' + 'Wrong Command: Local directory ends with backslash (\\)'
                ' Please wrap local directory between quotes and remove last backslash.')
        cleanedFileName = Utils.getFileName(local_file)
        if (not os.path.exists(local_file.replace(cleanedFileName,"")) and not os.path.exists(local_file)):
            raise Exception(
                '\n' + 'Wrong Command: ' + local_file +
                ' Provided local directory does not exists.\n'
                '               Please ensure the local directory exists.')
        if (os.path.isdir(local_file) or local_file.endswith("\\") or local_file.endswith("/")):
            local_file_name = SDPath(sdpath).dataset
            temp_path = os.path.join(local_file,local_file_name)
            print("\nLocal path is a directory, based on " + sdpath + ", local path will be " + temp_path + ". Continue? [y/n]", end='')
            sys.stdout.flush()
            confirm = sys.stdin.readline().rstrip().lower()
            if (confirm == 'y'):
                local_file = temp_path
            else:
                raise Exception('Please provide correct local path. ')

        if Utils.isDatasetPath(sdpath) is False:
            raise Exception(
                '\n' + 'Wrong Command: ' + sdpath +
                ' is not a valid seismic store dataset path.\n'
                '               A valid seismic store dataset path '
                'must be in this form '
                'sd://<tenant_name>/<subproject_name>/<path>*/<dataset_name>.'
                '\n               For more information type "python sdutil cp"'
                ' to open the command help menu.')

        sd = SeismicStoreService(self._auth)
        ds = Dataset.from_json(sd.dataset_lock(sdpath, "read"))
        if ds.filemetadata is None:
            raise Exception('Corrupted dataset ' + sdpath +
                            ', filemetadata not found.')
        if 'nobjects' not in ds.filemetadata:
            raise Exception('Corrupted dataset ' + sdpath +
                            ', unexpected filemetadata.')
        if ds.filemetadata['type'] != 'GENERIC':
            raise Exception('Dataset is of type ' + ds.filemetadata['type'] +
                            '. This type is not currently supported')
        storage_service = StorageFactory.build(
            sd.get_cloud_provider(sdpath), auth=self._auth)
        force=False
        if ((not keyword_args.force is None) and (keyword_args.force.lower()=='true')):
            force=True
        if (os.path.isfile(local_file) and (not force)):
                raise Exception('Local file ' + local_file + ' already exists. If you want to overwrite set the --force flag to True.')
        if (os.name == "nt"):
            if  ("c:" in local_file.lower() and not "\\" in local_file and not os.path.isdir(local_file)):
                local_file = os.path.join(os.getcwd(),local_file.replace("c:","").replace("C:",""))
            print("\nLocal file will be saved as " + local_file + ". Continue? [y/n]", end='')
            sys.stdout.flush()
            confirm = sys.stdin.readline().rstrip().lower()
            if (confirm != 'y'):
                raise Exception('\nPlease consider wrapping sdutil path and local file between quotes, some examples:'
                  ' cp "sd://tenant/subproject/folder/dataset" "c:\\\\Users\\\\MyUser\\\\Desktop\\\\file"'
                  ' cp "sd://tenant/subproject/folder/dataset" "file"')
        storage_service.download(local_file, ds)
        if ds.sbit is not None:
            sd.dataset_patch(sdpath, None, ds.sbit)

    def cp_local_to_sd(self, args, keyword_args):
        """ Copy a local file to seismic store
        """
        seismicmeta = None
        seismicmeta_file = None
        read_write_flag = None
        read_only_file_flag = None
        storage_tier = None

        if keyword_args.tier is not None:
            if str(keyword_args.tier).capitalize() not in ('Hot', 'Cool'):
                raise Exception(f'\'{keyword_args.tier}\' is not an acceptable Storage tier')
            storage_tier = str(keyword_args.tier).capitalize()
        tier = Tier(storage_tier)

        if keyword_args.seismicmeta is not None:
            seismicmeta_file = keyword_args.seismicmeta

            if seismicmeta_file is True:
                # flag given just as --seismicmeta with no =XXX
                print("seismicmeta argument declared but not defined")
                self.help()

        if keyword_args.read_only is not None:
            read_only_file_flag = True

        if keyword_args.read_write is not None:
            read_write_flag = True

        if read_only_file_flag and read_write_flag:
            raise Exception(
                '\n' + 'Wrong Command: '
                       'Both read-only and read-write flags cannot be passed at once'
                       '\n               For more information type "python sdutil cp"'
                       ' to open the command help menu.')

        chunk_size = 32
        if keyword_args.chunk_size is True: # discard option with no value (--chunk-size)
            raise Exception(
                '\n' + 'Wrong Command: '
                       'The chunk-size argument has been declared but not defined (not provided value)'
                       '\n               For more information type "python sdutil cp"'
                       ' to open the command help menu.')
        if keyword_args.chunk_size is not None:
            try:
                chunk_size = int(keyword_args.chunk_size)
            except ValueError: # discard option with value "not an int" (--chunk-size=test)
                raise Exception(
                    '\n' + 'Wrong Command: '
                           'The chunk-size argument must be an integer value greater than zero'
                           '\n               For more information type "python sdutil cp"'
                           ' to open the command help menu.')

            if chunk_size < 0:  # discard option with value < 0 (--chunk-size=-16)
                raise Exception(
                    '\n' + 'Wrong Command: '
                           'The chunk-size argument must be an integer value greater than zero'
                           '\n               For more information type "python sdutil cp"'
                           ' to open the command help menu.')

        local_file = None
        legal_tag = None
        sdpath = None

        local_file = args[0]

        if (Utils.isSDPath(args[-1]) and str(args[-1]).endswith("/")):
            cleanedFileName = Utils.getFileName(local_file)
            if (Utils.isDatasetPath(str(args[-1]) + cleanedFileName)):
                print("\nPath ends with '/', based on " + local_file + ", sdpath will be " + str(args[-1]) + cleanedFileName + ". Continue? [y/n]", end='')
                sys.stdout.flush()
                confirm = sys.stdin.readline().rstrip().lower()
                if (confirm == 'y'):
                    sdpath = str(args[-1]) + cleanedFileName
        elif (Utils.isSDPath(args[-2]) and str(args[-2]).endswith("/")):
            cleanedFileName = Utils.getFileName(local_file)
            if (Utils.isDatasetPath(str(args[-1]) + cleanedFileName)):
                print("\nPath ends with '/', based on " + local_file + ", sdpath will be " + str(args[-2]) + cleanedFileName + ". Continue? [y/n]", end='')
                sys.stdout.flush()
                confirm = sys.stdin.readline().rstrip().lower()
                if (confirm == 'y'):
                    sdpath = str(args[-2]) + cleanedFileName
                legal_tag = args[-1]
        elif (Utils.isDatasetPath(args[-1])):
            sdpath = args[-1]
        elif (Utils.isDatasetPath(args[-2])):
            sdpath = args[-2]
            legal_tag = args[-1]

        if Utils.isDatasetPath(sdpath) is False:
            if (Utils.isSDPath(args[-1])):
                sdpath = args[-1]
            elif (Utils.isSDPath(args[-2])):
                sdpath = args[-2]
            raise Exception(
                '\n' + 'Wrong Command: ' + sdpath +
                ' is not a valid seismic store dataset path.\n'
                '               A valid seismic store dataset path must be in '
                'this form '
                'sd://<tenant_name>/<subproject_name>/<path>*/<dataset_name>.'
                '\n               For more information type "python sdutil cp"'
                'to open the command help menu.')

        sd = SeismicStoreService(self._auth)
        if seismicmeta_file:
            with open(seismicmeta_file, 'r') as f:
                seismicmeta = json.load(f)
        ds = Dataset.from_json(sd.dataset_register(sdpath, None,
                                                   legal_tag, seismicmeta))

        if os.path.isfile(local_file) is False:
            raise Exception(
                '\n' + 'Wrong Command: ' + local_file +
                ' is not a valid local file name or '
                'the local file does not exist.\n' +
                'If you are providing full path of file with backslash,' +
                'please use double backslash.\n'
                '               For more information type "python sdutil cp"'
                ' to open the command help menu.')
        storage_service = StorageFactory.build(
            sd.get_cloud_provider(sdpath), auth=self._auth)

        try:
            upload_response = storage_service.upload(local_file, ds, storage_tier=tier, chunk_size=chunk_size)
        except Exception:
            print('Error encountered during upload, deleting the partially created record from seismic store')
            sd.dataset_delete(sdpath)
            raise

        if "num_of_objects" in upload_response:
            patch = {
                'filemetadata': {
                    'type': 'GENERIC',
                    'size':  os.path.getsize(local_file),
                    'nobjects': upload_response["num_of_objects"],
                    'md5Checksum': upload_response.get("md5_checksum", None),
                    'tier_class': upload_response.get("blob_tier")
                }
            }

            if read_write_flag:
                patch['readonly'] = False
            elif sdpath.endswith(tuple(Config.get_readonly_file_formats())) or read_only_file_flag:
                patch['readonly'] = True
            sd.dataset_patch(sdpath, patch, ds.sbit)
        else:
            sd.dataset_delete(sdpath)
