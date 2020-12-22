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


class App(SDUtilCMD):

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

        cmd = args[0]
        args.pop(0)

        command = {
            "register": self.register,
            "set-trusted": self.set_trusted,
            "list": self.list,
            "list-trusted": self.list_trusted
        }.get(cmd, None)

        if command is None:
            raise Exception(
                '\n' +
                'Wrong Command: ' + cmd + ' is not a valid command.\n' +
                '               The valid arguments are register, set-trusted,'
                ' list and list-trusted.\n'
                '               For more information type "python sdutil app"'
                ' to open the command help menu.')
        command(args, keyword_args)

    def register(self, args, keyword_args):
        if not args:
            self.help()

        svcemail = args[0]
        args.pop(0)

        # check that it's a valid email
        if Utils.isValidEmail(svcemail) is False:
            raise Exception(
                '\n' +
                'Wrong Command: ' + svcemail +
                ' is not a valid email.\n'
                '               For more information type "python sdutil app"'
                ' to open the command help menu.')

        if not args:
            self.help()

        sdpath = args[0]
        args.pop(0)

        if Utils.isTenant(sdpath) is False:
            raise Exception(
                '\n' +
                'Wrong Command: ' + sdpath +
                ' is not a valid seismic store tenant path.\n'
                '               For more information type "python sdutil app"'
                ' to open the command help menu.')

        print('')
        print('> Registering ' + svcemail + ' as seismic store app... ',
              end='')
        sys.stdout.flush()
        SeismicStoreService(self._auth).app_register(svcemail, sdpath)
        print('OK')
        sys.stdout.flush()

    def set_trusted(self, args, keyword_args):
        if not args:
            self.help()

        svcemail = args[0]
        args.pop(0)

        # check that it's a valid email
        if Utils.isValidEmail(svcemail) is False:
            raise Exception(
                '\n' +
                'Wrong Command: ' + svcemail +
                ' is not a valid email.\n'
                '               For more information type "python sdutil app"'
                ' to open the command help menu.')

        if not args:
            self.help()

        sdpath = args[0]
        args.pop(0)

        if Utils.isTenant(sdpath) is False:
            raise Exception(
                '\n' +
                'Wrong Command: ' + sdpath +
                ' is not a valid seismic store tenant path.\n'
                '               For more information type "python sdutil app"'
                ' to open the command help menu.')

        print('')
        print('> Registering ' + svcemail
              + ' as seismic store trusted app... ', end='')
        sys.stdout.flush()
        SeismicStoreService(self._auth).apptrusted_register(svcemail, sdpath)
        print('OK')
        sys.stdout.flush()

    def list(self, args, keyword_args):

        if not args:
            self.help()

        sdpath = args[0]
        args.pop(0)

        if Utils.isTenant(sdpath) is False:
            raise Exception(
                '\n' +
                'Wrong Command: ' + sdpath +
                ' is not a valid seismic store tenant path.\n'
                '               For more information type "python sdutil app"'
                ' to open the command help menu.')

        res = SeismicStoreService(self._auth).app_list(sdpath)
        if len(res) > 0:
            print('')

        for item in res:
            print(' - ' + item)

    def list_trusted(self, args, keyword_args):
        if not args:
            self.help()

        sdpath = args[0]
        args.pop(0)

        if Utils.isTenant(sdpath) is False:
            raise Exception(
                '\n' +
                'Wrong Command: ' + sdpath +
                ' is not a valid seismic store tenant path.\n'
                '               For more information type "python sdutil app"'
                ' to open the command help menu.')

        res = SeismicStoreService(self._auth).apptrusted_list(sdpath)
        if len(res) > 0:
            print('')

        for item in res:
            print(' - ' + item)
