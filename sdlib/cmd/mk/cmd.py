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

from sdlib.api.seismic_store_service import SeismicStoreService
from sdlib.api.storage_service import StorageFactory
from sdlib.cmd.cmd import SDUtilCMD
from sdlib.cmd.helper import CMDHelper
from sdlib.shared.utils import Utils


class Mk(SDUtilCMD):
    def __init__(self, auth):
        self._auth = auth

    @staticmethod
    def help():
        reg = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reg.json')
        CMDHelper.cmd_help(reg)

    def execute(self, args, keyword_args):

        if not args:
            self.help()

        sdpath = args[0]
        args.pop(0)

        if Utils.isSubProject(sdpath):
            self.mk_subproject(sdpath, args, keyword_args)
        else:
            raise Exception('\n' + 'Wrong Command: ' + sdpath + ' is not a valid subproject path.\n'
                            '               The valid arguments is '
                            'sd://<tenant_name>/<subproject_name>.\n'
                            '               For more information type "python sdutil mk"'
                            ' to open the command help menu.')

    def mk_subproject(self, sdpath, args, keyword_args: dict):
        if len(args) < 2:
            self.help()
        owner_email = str(args[0]).lower()
        legal_tag = str(args[1])

        print('')

        sd = SeismicStoreService(self._auth)
        cloud_provider = sd.get_cloud_provider(sdpath)

        cl = None
        loc = None
        if (cloud_provider == "google"):

            storage_provider = StorageFactory.build(sd.get_cloud_provider(sdpath), auth=self._auth)

            for idx, cl in enumerate(storage_provider.get_storage_classes()):
                print("[" + str(idx + 1) + "] " + cl)
            print("\nSelect the bucket storage class: ", end='')
            sys.stdout.flush()
            idx = sys.stdin.readline()
            try:
                idx = int(idx)
            except Exception:
                raise Exception("\nInvalid choice.")
            if idx < 1 or idx > len(storage_provider.get_storage_classes()):
                raise Exception("\nInvalid choice.")
            cl = storage_provider.get_storage_classes()[idx - 1]

            if cl == 'REGIONAL':
                locs = storage_provider.get_storage_regions()
            elif cl == 'MULTI_REGIONAL':
                locs = storage_provider.get_storage_multi_regions()
            else:
                locs = storage_provider.get_storage_multi_regions() + storage_provider.get_storage_regions()

            print('')

            for idx, loc in enumerate(locs):
                print("[" + str(idx + 1) + "] " + loc)
            print("\nSelect the bucket storage location: ", end='')
            sys.stdout.flush()
            idx = sys.stdin.readline()
            try:
                idx = int(idx)
            except Exception:
                raise Exception("\nInvalid choice.")
            if idx < 1 or idx > len(locs):
                raise Exception("\nInvalid choice.")
            loc = locs[idx - 1]

        tenant = Utils.getTenant(sdpath)
        subproject = Utils.getSubproject(sdpath)

        if ('access_policy' in keyword_args.__dict__):
            access_policy = getattr(keyword_args, 'access_policy')
            if (access_policy == 'dataset'):
                res = input('Are you sure the access policy is dataset?\nIf you set it to dataset access policy, then you will be unable to update it to "uniform" later.\nEnter (y/n): ')
                if res.lower().strip()[:1] != "y":
                    sys.exit(1)
        else:
            access_policy = 'uniform'
        admins = None
        viewers = None

        if ('admin_acl' in keyword_args.__dict__):
            admins = getattr(keyword_args, 'admin_acl')
        
        if ('viewer_acl' in keyword_args.__dict__):
            viewers = getattr(keyword_args, 'viewer_acl')

        print('')
        message = ('> Registering the subproject {subproject}(tenant={tenant})' ' with {owner} as admin ... ')
        print(message.format(**{"subproject": subproject, "tenant": tenant, "owner": owner_email}), end='')
        sys.stdout.flush()

        sd.create_subproject(tenant, subproject, owner_email, cl, loc, legal_tag, access_policy, admins, viewers)

        print('OK')
        sys.stdout.flush()
