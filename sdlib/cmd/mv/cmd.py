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


class Mv(SDUtilCMD):

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

            sdpath_from = str(args[0])
            sdpath_to = str(args[1])

            if Utils.isDatasetPath(sdpath_from) is False:
                raise Exception(
                    '\n' +
                    'Wrong Command: ' + sdpath_from +
                    ' is not a valid seismic store dataset path.\n'
                    '               A valid seismic store dataset path '
                    'must be in this form '
                    'sd://<tenant_name>/<subproject_name>/<path>*/<dataset_name>.\n'   # noqa E501
                    '               For more information type '
                    '"python sdutil cp" to open the command help menu.')

            if Utils.isDatasetPath(sdpath_to) is False:
                raise Exception(
                    '\n' +
                    'Wrong Command: ' + sdpath_to +
                    ' is not a valid seismic store dataset path.\n' +
                    '               A valid seismic store dataset path '
                    'must be in this form '
                    'sd://<tenant_name>/<subproject_name>/<path>*/<dataset_name>.\n' +  # noqa E501
                    '               For more information type '
                    '"python sdutil cp" to open the command help menu.')

            print('')
            print('> Moving the dataset %s to %s ...'
                  % (sdpath_from, sdpath_to), end='')
            sys.stdout.flush()

            sd = SeismicStoreService(self._auth) 
            SeismicStoreService(self._auth).dataset_cp(sdpath_from, sdpath_to)
            sd.dataset_delete(sdpath_from)

            print('OK')
            sys.stdout.flush()
