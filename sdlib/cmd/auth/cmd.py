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
import errno

from sdlib.cmd.cmd import SDUtilCMD
from sdlib.cmd.helper import CMDHelper


class Auth(SDUtilCMD):

    def __init__(self, auth=None):
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

        if cmd == 'login':
            self._auth.login()
            return

        if cmd == 'logout':
            self._auth.logout()
            return

        if cmd == "activate-service-account":

            self.activate_service_account(keyword_args)
            return

        if cmd == "deactivate-service-account":

            self.deactivate_service_account(keyword_args)
            return

        if cmd == 'idtoken':

            idtoken = self._auth.get_id_token()
            print('\n' + idtoken)
            return

        raise Exception(
            '\n'
            'Wrong Command: ' + cmd + ' is not a valid argument.\n'
            '               The valid arguments are:\n                  login,'
            ' logout, activate-service-account, deactivate-service-account and idtoken.\n'
            '               For more information type "python sdutil auth"'
            ' to open the command help menu.')

    def activate_service_account(self, keyword_args):

        if keyword_args.key_file is None or keyword_args.key_file is True:
            raise Exception(
                "\nWrong Command: missing required argument --key-file=PATH_TO_KEY.json\n"
                '               For more information type "python sdutil auth" to open the command help menu.')

        if not os.path.exists(keyword_args.key_file):
            raise Exception("\nKey file doesn't exist: %s"% keyword_args.key_file)

        full_path = os.path.abspath(keyword_args.key_file)

        # ensure the directory for contain it exists or create it
        try:
            os.makedirs(os.path.dirname(self._auth.get_service_account_file()))
        except OSError as e:
            if e.errno == errno.EEXIST:
                pass
                
        with open(self._auth.get_service_account_file(), "w") as auth_fh:
            json.dump({"service-account-key-file": full_path}, auth_fh, indent=4)

        return

    def deactivate_service_account(self, keyword_args):
        
        try:
            os.remove(self._auth.get_service_account_file())
        except OSError as e:
            if e.errno == errno.ENOENT:
                # ignore file doesn't exist
                pass
        return