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

import sys
import os

from sdlib.cmd.cmd import SDUtilCMD
from sdlib.cmd.helper import CMDHelper
from sdlib.shared.utils import Utils
from sdlib.api.seismic_store_service import SeismicStoreService


class Ls(SDUtilCMD):

    def __init__(self, auth):
        self._auth = auth

    @staticmethod
    def help():
        reg = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           'reg.json')
        CMDHelper.cmd_help(reg)

    def execute(self, args, keyword_args):

        if not args:
            self.help()

        recursive_flag = any([keyword_args.r, keyword_args.recursive,
                              keyword_args.lr, keyword_args.rl])
        full_path_flag = any([keyword_args.l, keyword_args.full_path,
                              keyword_args.long, keyword_args.lr,
                              keyword_args.rl])
        names = args

        for sdpath in names:
            # If multiple command line arguments, show which arg
            # we are processing. Similar to the recursive mode.
            if len(names) > 1 and not recursive_flag:
                print('')
                print(sdpath + "/")
            print('')
            self.executeLs(sdpath, None, recursive_flag, full_path_flag)

    def executeLs(self, sdpath, provider, recursive_flag, full_path_flag):

        if Utils.isSDPath(sdpath) is False:
            raise Exception(
                '\n' +
                'Wrong Command: ' + sdpath +
                ' is not a valid seismic store path.\n' +
                '               The seismic store dataset path should '
                'match the standard form '
                'sd://<tenant_name>/<subproject_name>/<path>/<dataset_name>.\n'
                '               For more information type "python sdutil ls"'
                ' to open the command help menu.')

        seismicStoreClient = SeismicStoreService(self._auth)
        if provider is None:
            res, headers = seismicStoreClient.status()
            provider = headers['Service-Provider']

        if provider == 'azure':

            next_page_cursor = None
            limit = 10000
            working_mode = 'all'
            while True:

                res = seismicStoreClient.ls(
                    sdpath, limit=limit, next_page_cursor=next_page_cursor, working_mode=working_mode)

                if sdpath == 'sd://' or Utils.isTenant(sdpath):
                    for item in res:
                        if full_path_flag:
                            print(sdpath + "/" + item)
                        else:
                            print(item)
                    return

                # folders returned with the first call, after only  pagination calls for datasets  
                working_mode = 'datasets'

                # The backend returns all the sub-folders before the datasets.
                # Keep this behavior for backwards compatibility.
                # Apart from that the items are returned in an arbitrarily
                # scrambled order. I want them sorted to improve usability.
                dirs = sorted([e for e in res['datasets'] if e[-1] == '/'])
                datasets = sorted([e for e in res['datasets'] if e[-1] != '/'])

                for item in (list(dirs) + list(datasets)):

                    # If this item represents a folder or a subproject, set "folder"
                    # to the name (sans trailing slash) of that folder.
                    if "/" not in sdpath[5:]:
                        folder = item
                    elif item[-1] == '/':
                        folder = item[:-1]
                    else:
                        folder = None

                    # Print the item (file or folder) itself, except for -lr
                    # where we don't show folders at all.
                    if recursive_flag and full_path_flag and folder:
                        pass
                    elif full_path_flag or (recursive_flag and folder):
                        print(sdpath + "/" + item)
                    else:
                        print(item)

                    if recursive_flag and folder:
                        self.executeLs(sdpath + "/" + folder, provider, recursive_flag, full_path_flag)

                sys.stdout.flush()

                if 'nextPageCursor' not in res or res['nextPageCursor'] is None:
                    break

                next_page_cursor = res['nextPageCursor']
        
        else: # provider != 'azure' // for these pagination of the ls method should be checked/reviewed
            
            res = seismicStoreClient.ls(sdpath)

            # The backend returns all the sub-folders before the datasets.
            # Keep this behavior for backwards compatibility.
            # Apart from that the items are returned in an arbitrarily
            # scrambled order. I want them sorted to improve usability.
            dirs = sorted([e for e in res if e[-1] == '/'])
            datasets = sorted([e for e in res if e[-1] != '/'])

            if not recursive_flag:
                print('')

            for item in (list(dirs) + list(datasets)):
                # If this item represents a folder or a subproject, set "folder"
                # to the name (sans trailing slash) of that folder.
                if "/" not in sdpath[5:]:
                    folder = item
                elif item[-1] == '/':
                    folder = item[:-1]
                else:
                    folder = None
                # Print the item (file or folder) itself, except for -lr
                # where we don't show folders at all.
                if recursive_flag and full_path_flag and folder:
                    pass
                elif full_path_flag or (recursive_flag and folder):
                    print(sdpath + "/" + item)
                else:
                    print(item)
                if recursive_flag and folder:
                    self.executeLs(sdpath + "/" + folder, recursive_flag,
                                full_path_flag)
                    if not (recursive_flag and full_path_flag):
                        print('')

            sys.stdout.flush()
