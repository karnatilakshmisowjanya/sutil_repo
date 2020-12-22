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
            self.executeLs(sdpath, recursive_flag, full_path_flag)

    def executeLs(self, sdpath, recursive_flag, full_path_flag):

        if Utils.isSDPath(sdpath) is False:
            raise Exception(
                '\n' +
                'Wrong Command: ' + sdpath +
                ' is not a valid seismic store path.\n' +
                '               The seismic store dataset path should '
                'match the standard form '
                'sd://<tenant_nane>/<subproject_name>/<path>/<dataset_name>.\n'
                '               For more information type "python sdutil ls"'
                ' to open the command help menu.')

        res = SeismicStoreService(self._auth).ls(sdpath)

        # The backend returns all the subfolders before the datasets.
        # Keep this behavior for backwards compatibility.
        # Apart from that the items are returned in an arbitrarily
        # scrambled order. I want them sorted to improve usability.
        res_1st = sorted([e for e in res if e[-1] == '/'])
        res_2nd = sorted([e for e in res if e[-1] != '/'])
        res = list(res_1st) + list(res_2nd)

        if not recursive_flag:
            print('')
        for item in res:
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