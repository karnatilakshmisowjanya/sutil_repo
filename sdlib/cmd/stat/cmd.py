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
from sdlib.cmd.cmd import SDUtilCMD
from sdlib.cmd.helper import CMDHelper
from sdlib.shared.utils import Utils


class Stat(SDUtilCMD):

    def __init__(self, auth):
        self._auth = auth

    @staticmethod
    def help():
        CMDHelper.cmd_help(os.path.join(os.path.dirname(
            os.path.abspath(__file__)), 'reg.json'))

    def execute(self, args, keyword_args):

        detailed_flag = any([keyword_args.detailed, keyword_args.d])

        if not args:
            self.help()

        names = []
        for arg in args:
            if arg[0] != "-":
                names.append(arg)

        for sdpath in names:
            self.executeStat(sdpath, detailed_flag)

    def executeStat(self, sdpath, detailed_flag):

        if Utils.isTenant(sdpath):
            self.display_tenant(sdpath)
        elif Utils.isSubProject(sdpath):
            self.display_subproject(sdpath)
        elif Utils.isDatasetPath(sdpath):
            self.display_dataset(sdpath, detailed_flag)
        else:
            # Catch invalid sdpaths [sd:// or other malformed paths]
            raise Exception(
                '\n' +
                'Wrong Command: ' + sdpath +
                ' is not a valid seismic store dataset path.\n' +
                '               The seismic store dataset path should '
                'match one of the standard forms: \n' +
                ' ' * 15 + 'Tenant: sd://<tenant_nane>.\n' +
                ' ' * 15 + 'Subproject: sd://<tenant_nane>/<subproject_name>.\n' +  # noqa E501
                ' ' * 15 + 'Dataset: sd://<tenant_nane>/<subproject_name>/<path>/<dataset_name>.\n' +  # noqa E501
                ' ' * 15 + 'For more information type "python sdutil stat" to open the command help menu.')  # noqa E501

    def display_tenant(self, sdpath):
        # Display tenant data
        res = SeismicStoreService(self._auth).get_tenant(
            Utils.getTenant(sdpath))
        print('')
        print(' - Uri: ' + sdpath)
        print(' - Domain: ' + res['esd'])
        print(' - Project Id: ' + res['gcpid'])
        sys.stdout.flush()

    def display_subproject(self, sdpath):
        # Display subproject data
        res = SeismicStoreService(self._auth).get_subproject(
            Utils.getTenant(sdpath), Utils.getSubproject(sdpath))
        print('')
        print(' - Uri: ' + sdpath)
        if 'ltag' in res:
            print(' - Legal Tag: ' + res['ltag'])
        if 'storage_class' in res:
            print(' - Storage Class: ' + res['storage_class'])
        if 'storage_location' in res:
            print(' - Storage Location: ' + res['storage_location'])
        
        print(' - Access Policy: ' +  res['access_policy'])
        print(' - ACLs: ' +  json.dumps(res['acls']))
        sys.stdout.flush()

    def display_dataset(self, sdpath, detailed_flag):
        # Display dataset data
        ds = Dataset.from_json(SeismicStoreService(
            self._auth).dataset_get(sdpath, str(detailed_flag).lower()))
        print('')
        print(' - Name: ' + 'sd://' + ds.tenant +
              '/' + ds.subproject + ds.path + ds.name)
        if ds.dstype is not None:
            print(' - Type: ' + ds.dstype)
        print(' - Created By: ' + ds.created_by)
        print(' - Created Date: ' + ds.created_date)
        if ds.filemetadata is not None:
            if 'size' in ds.filemetadata:
                print(' - Size: ' + Utils.sizeof_fmt(ds.filemetadata['size']))
            if 'nobjects' in ds.filemetadata and detailed_flag:
                print(' - No of Objects: ' + str(ds.filemetadata['nobjects']))
        if detailed_flag and ds.legaltag is not None:
            print(' - Legal Tag: ' + ds.legaltag)
        
        if ds.readonly is True:
            print(' - ReadOnly: True')
        else:
            print(' - ReadOnly: False')
        
        if detailed_flag and ds.sbit is not None:
            if str(ds.sbit).startswith('R'):
                print(' - Lock Mode: read')
            else:
                print(' - Lock Mode: write (' + ds.sbit + ')')
            print(' - Lock Counter: ' + str(ds.sbit_count))
        if detailed_flag and ds.seismicmeta is not None:
            print(' - Seismic record : ', end="")
            print(ds.seismicmeta)

        if ds.transfer_status is not None:
            print(' - Copy Transfer Status: ', end="")
            print(ds.transfer_status)
            
        sys.stdout.flush()
