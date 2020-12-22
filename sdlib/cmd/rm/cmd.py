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


class Rm(SDUtilCMD):

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

        for sdpath in args:
            self.executeRm(sdpath)

    def executeRm(self, sdpath):

        print('')

        if Utils.isDatasetPath(sdpath):
            print('> Deleting the dataset ' + sdpath + ': ', end='')
            sys.stdout.flush()
            SeismicStoreService(self._auth).dataset_delete(sdpath)
        elif Utils.isSubProject(sdpath):
            print('> Deleting the subproject ' + sdpath + ': ', end='')
            sys.stdout.flush()
            SeismicStoreService(self._auth).delete_subproject(
                Utils.getTenant(sdpath), Utils.getSubproject(sdpath))
        else:
            raise Exception(
                '\n' +
                'Wrong Command: ' + sdpath +
                ' is not a valid seismic store dataset or subproject path.\n'
                '               The seismic store path should match the '
                'standard form '
                'sd://<tenant_nane>/<subproject_name>/<path>/<dataset_name>.\n'
                '               For more information type "python sdutil rm"'
                ' to open the command help menu.')

        print('OK')
        sys.stdout.flush()
