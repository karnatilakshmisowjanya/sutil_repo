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

import json
import os

from sdlib.api.seismic_store_service import SeismicStoreService
from sdlib.cmd.cmd import SDUtilCMD
from sdlib.cmd.helper import CMDHelper
from sdlib.shared.utils import Utils
from sdlib.shared.config import Config


class Patch(SDUtilCMD):
    def __init__(self, auth):
        self._auth = auth

    @staticmethod
    def help():
        reg = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'reg.json')
        CMDHelper.cmd_help(reg)

    def execute(self, args, keyword_args):

        if len(args) < 1:
            self.help()

        if (Utils.isDatasetPath(args[-1]) or Utils.isSubProject(args[-1]) ):
            self.patch(args, keyword_args)
        else:
            raise Exception(
                '\n' +
                'Wrong Command: the patch command cannot be applied on seistore tenant.\n' +
                '               For more information type "python sdutil patch"'
                ' to open the command help menu.')

    def patch(self, args, keyword_args):

        dataset_patch_body = {}
        subproject_ltag = None
        sdpath = args[0]

        # storage tier
        storage_tier = keyword_args.tier
        if storage_tier is not None:
            if str(Config.get_cloud_provider()) != "azure":
                raise Exception(f'The tier patch is not supported for the \'{Config.get_cloud_provider()}\' cloud provider.')
            
            # not storage tier patch on subproject
            if Utils.isSubProject(sdpath):
                raise Exception(
                    '\n' +
                    'Wrong Command: the tier patch cannot be applied to subproject.\n' +
                    '               For more information type "python sdutil patch"'
                    ' to open the command help menu.')
            
            if str(storage_tier).capitalize() not in ('Hot', 'Cool', 'Cold'):
                raise Exception(f'\'{keyword_args.tier}\' is not an acceptable Storage tier. Your options are [Hot, Cool, Cold]')
            storage_tier = str(storage_tier).capitalize()
            dataset_patch_body["change_tier"] = storage_tier

        # seismic meta
        seismicmeta_file = keyword_args.seismicmeta
        if seismicmeta_file is not None:

            # validate seismic meta
            if seismicmeta_file is True or len(seismicmeta_file) == 0:
                # flag given as -seismicmeta or --seismicmeta or --seismicmeta=
                # the required form is --seismicmeta=XXX
                self.help()

            # not seismic meta patch on subproject
            if Utils.isSubProject(sdpath):
                raise Exception(
                    '\n' +
                    'Wrong Command: the seismicmeta patch cannot be applied to subproject.\n' +
                    '               For more information type "python sdutil patch"'
                    ' to open the command help menu.')

            # load the seismic meta
            with open(seismicmeta_file, 'r') as f:
                dataset_patch_body["seismicmeta"] = json.load(f)                    

        # legal tag
        legal_tag = keyword_args.ltag
        if legal_tag is not None:

            # validate legal tag
            if legal_tag is True or len(legal_tag) == 0:
                # flag given as -ltag or --ltag or --ltag=
                # the required form is --ltag=XXX
                self.help()

            # load the legal tag
            if Utils.isDatasetPath(sdpath):
                dataset_patch_body["ltag"] = legal_tag
            else:
                subproject_ltag = legal_tag

        # readonly
        readonly = keyword_args.readonly
        if readonly is not None:

            # validate readonly 
            if readonly is True or len(readonly) == 0:
                # flag given as -readonly or --readonly or --readonly=
                # the required form is --readonly=XXX
                self.help()
            
            # not seismic meta patch on subproject
            if Utils.isSubProject(sdpath):
                raise Exception(
                    '\n' +
                    'Wrong Command: the readonly mode cannot be applied to a subproject.\n' +
                    '               For more information type "python sdutil patch"'
                    ' to open the command help menu.')
            
            readonly = str(readonly).lower()

            # validate the readonly value 
            if(readonly != 'true' and readonly != 'false'):
                self.help()

            dataset_patch_body["readonly"] = True if readonly == 'true' else False

        # patch the dataset
        if Utils.isDatasetPath(sdpath):

            # the patch method for dataset require at least a body field
            if len(dataset_patch_body) == 0:
                self.help()

            # patch the dataset
            print('\n Patching the dataset ' + sdpath + ': ', end='')
            SeismicStoreService(self._auth).dataset_patch(sdpath, dataset_patch_body, None)
            print('OK')

        else: # patch the subproject

            # the patch method for subnproject require the ltag
            if subproject_ltag is None:
                self.help()
            
            admins = None
            viewers = None

            if ('admin_acl' in keyword_args.__dict__):
                admins = getattr(keyword_args, 'admin_acl')
            
            if ('viewer_acl' in keyword_args.__dict__):
                viewers = getattr(keyword_args, 'viewer_acl')

            # patch the subproject
            print('\n Patching the subproject ' + sdpath + ': ', end='')
            SeismicStoreService(self._auth).patch_subproject(sdpath, subproject_ltag, keyword_args.recursive, keyword_args.access_policy, admins, viewers)
            print('OK')
