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

import os

from sdlib.api.seismic_store_service import SeismicStoreService
from sdlib.cmd.cmd import SDUtilCMD
from sdlib.cmd.helper import CMDHelper
from sdlib.shared.config import Config
from sdlib.shared.utils import Utils


class Op(SDUtilCMD):
    def __init__(self, auth):
        self._auth = auth
 
    @staticmethod
    def help():
        reg = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           'reg.json')
        CMDHelper.cmd_help(reg)

    def execute(self, args, keyword_args):

        if len(args) < 1:
            self.help()

        if args[0] == 'bulk-delete':
            self.bulkDelete(args, keyword_args)
        elif args[0] == 'bulk-delete-status':
            self.bulkDeleteStatus(args, keyword_args)
        else:
            raise Exception(
                '\n' +
                'Wrong Command:\n'
                'For more information type "python sdutil op"'
                ' to open the command help menu.')

    def bulkDelete(self, args, keyword_args):

        sdpath = self.pathCheck(keyword_args)

        if not Utils.isDatasetPath(sdpath) and not Utils.isSubProject(sdpath):
            raise Exception(
                '\n' +
                'Incorrect SDPath format: sd://<tenant>/<subproject>/<path>*/\n' +
                'or\n' +
                'sd://<tenant>/<subproject>/<path>*/<dataset-name>')

        if str(Config.get_cloud_provider()) != "azure":
            raise Exception(f'The bulk-delete is not supported for the \'{Config.get_cloud_provider()}\' cloud provider.')

        print('\n Requesting bulk delete for ' + sdpath)
        response = SeismicStoreService(self._auth).operation_bulkDelete(sdpath)
        print('')
        print(' - Operation Id: ' + response['operation_id'])
    
    def bulkDeleteStatus(self, args, keyword_args):

        if len(args) < 3:
            raise Exception(
                '\n' +
                'Usage:\n'
                'python sdutil op bulk-delete-status [dataPartitionId] [operationId] (options)')

        dataPartitionId = args[1]
        operationId = args[2]

        if str(Config.get_cloud_provider()) != "azure":
            raise Exception(f'The bulk-delete is not supported for the \'{Config.get_cloud_provider()}\' cloud provider.')

        response = SeismicStoreService(self._auth).operation_bulkDeleteStatus(operationId, dataPartitionId)
        print('')
        print(' - Operation Id: ' + response['operation_id'])
        print(' - Status: ' + response['status'])
        print(' - Dataset Count: ' + str(response['dataset_cnt']))
        print(' - Completed Count: ' + str(response['completed_cnt']))
        print(' - Failed Count: ' + str(response['failed_cnt']))
        
    def changeTier(self, args, keyword_args):

        sdpath = self.pathCheck(keyword_args)

        if not Utils.isDatasetPath(sdpath) and not Utils.isSubProject(sdpath):
            raise Exception(
                '\n' +
                'Incorrect SDPath format: sd://<tenant>/<subproject>/<path>*/\n' +
                'or\n' +
                'sd://<tenant>/<subproject>/<path>*/<dataset-name>')

        if len(args) < 2:
            raise Exception(
                '\n' +
                'Usage:\n'
                'python sdutil op tier-change [ --path | --dataset ] [tier] (options)')

        tier = args[1]

        # storage tier
        storage_tier = tier
        if storage_tier is not None:
            if str(Config.get_cloud_provider()) != "azure":
                raise Exception(f'The bulk tier-change is not supported for the \'{Config.get_cloud_provider()}\' cloud provider.')
            
            
            if str(storage_tier).capitalize() not in ('Hot', 'Cool', 'Cold', 'Archive'):
                raise Exception(f'\'{tier}\' is not an acceptable Storage tier. Your options are [Hot, Cool, Cold, Archive]')
            storage_tier = str(storage_tier).capitalize()

        print('\n Requesting tier change of ' + sdpath + ' to tier ( ' + storage_tier + ' )')
        response = SeismicStoreService(self._auth).operation_changeTier(sdpath, storage_tier)
        print('')
        print(' - Operation Id: ' + response['operation_id'])
    
    def changeTierStatus(self, args, keyword_args):

        if len(args) < 3:
            raise Exception(
                '\n' +
                'Usage:\n'
                'python sdutil op tier-change-status [dataPartitionId] [operationId] (options)')

        dataPartitionId = args[1]
        operationId = args[2]

        if str(Config.get_cloud_provider()) != "azure":
            raise Exception(f'The bulk tier-change is not supported for the \'{Config.get_cloud_provider()}\' cloud provider.')

        response = SeismicStoreService(self._auth).operation_changeTierStatus(operationId, dataPartitionId)
        print('')
        print(' - Operation Id: ' + response['operation_id'])
        print(' - Status: ' + response['status'])
        print(' - Dataset Count: ' + str(response['dataset_cnt']))
        print(' - Completed Count: ' + str(response['completed_cnt']))
        print(' - Failed Count: ' + str(response['failed_cnt'])) 
    
    def pathCheck(self, keyword_args):
        if keyword_args.path is None and keyword_args.dataset is None:
            raise Exception(
                '\n' +
                'A SDPath (--path=) or SDDatasetPath (--dataset=) must be provided')

        if keyword_args.path is not None and keyword_args.dataset is not None:
            raise Exception(
                '\n' +
                'Provide only ONE SDPath (--path=) or SDDatasetPath (--dataset=)')
        
        if keyword_args.path is not None:
            sdpath = str(keyword_args.path)
            sdpath = sdpath + '/' if not (sdpath.endswith('/')) else sdpath
            return sdpath
        else:
            sdpath = str(keyword_args.dataset)
            sdpath = sdpath[:-1] if (sdpath.endswith('/')) else sdpath
            return sdpath
