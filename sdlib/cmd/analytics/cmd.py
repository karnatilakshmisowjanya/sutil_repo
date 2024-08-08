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
import re

from sdlib.api.seismic_store_service import SeismicStoreService
from sdlib.api.storage_service import StorageFactory
from sdlib.cmd.cmd import SDUtilCMD
from sdlib.cmd.helper import CMDHelper
from sdlib.shared.config import Config
from sdlib.shared.utils import Utils

class Analytics(SDUtilCMD):
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
            
        if args[0] == 'list':
            self.analyticsListReports(args, keyword_args)
        elif args[0] == 'download':
            self.analyticsDownloadReports(args, keyword_args)
        else:
            raise Exception(
                '\n' +
                'Wrong Command:\n'
                'For more information type "python sdutil analytics"'
                ' to open the command help menu.'
            )
    
    def analyticsListReports(self, args, keyword_args):
        if len(args) < 3:
            raise Exception(
                '\n' +
                'Usage:\n'
                'python sdutil analytics list [dataPartitionId] [subproject] (options)'
                '\nFor more information type "python sdutil analytics"'
                ' to open the command help menu.'
            )

        dataPartitionId = args[1]
        subproject = args[2]
        filter = keyword_args.filter
        extension = keyword_args.extension
        
        if str(Config.get_cloud_provider()) != "azure":
            raise Exception(f'The analytics feature is not supported for the \'{Config.get_cloud_provider()}\' cloud provider.')

        if filter and not re.match(r'^\d{4}(-\d{2}){0,2}$', filter):
            raise Exception(
                '\n' +
                'Usage:\n'
                'python sdutil analytics list [dataPartitionId] [subproject] (options)'
                '\nFor more information type "python sdutil analytics"'
                ' to open the command help menu.'
            )

        response = SeismicStoreService(self._auth).analytics_list_report(dataPartitionId, subproject, filter, extension)
        print(response)

    def analyticsDownloadReports(self, args, keyword_args):
        if len(args) < 3:
            raise Exception(
                '\n' +
                'Usage:\n'
                'python sdutil analytics download [dataPartitionId] [subproject] (options)'
                '\nFor more information type "python sdutil analytics"'
                ' to open the command help menu.'
            )
        sd = SeismicStoreService(self._auth) 
        dataPartitionId = args[1]
        subproject = args[2]
        filter = keyword_args.dates
        path = keyword_args.path
        extension = keyword_args.extension

        if str(Config.get_cloud_provider()) != "azure":
            raise Exception(
                f'The analytics feature is not supported for the \'{Config.get_cloud_provider()}\' cloud provider.')

        date = None 
        if filter == None or filter.upper() == 'ALL': 
            date = None
        elif filter.upper() != 'ALL' and re.match(r'^\d{4}(-\d{2}){0,2}$', filter):
            date = filter
        else:
            raise Exception(
                '\n' +
                'Usage:\n'
                'python sdutil analytics download [dataPartitionId] [subproject] (options)'
                '\nFor more information type "python sdutil analytics"'
                ' to open the command help menu.'
            )

        response = SeismicStoreService(self._auth).analytics_download_report(
            dataPartitionId, subproject, date, extension)

        storage_service = StorageFactory.build(
            sd.get_cloud_provider('azure'), auth=self._auth)

        if not filter:
            storage_service.download_object(response, local_path=path, latest=True)
        else:
            storage_service.download_object(response, local_path=path)
