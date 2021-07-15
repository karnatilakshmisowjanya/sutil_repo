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
from sdlib.cmd.cmd import SDUtilCMD
from sdlib.cmd.helper import CMDHelper
from sdlib.shared.config import Config
from sdlib.shared.sdpath import SDPath
from sdlib.shared.utils import Utils


class User(SDUtilCMD):

    def __init__(self, auth):
        self._auth = auth

    @staticmethod
    def help():
        reg = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                           "reg.json"))
        CMDHelper.cmd_help(reg)

    def execute(self, args, keyword_args):

        if not args:
            self.help()

        command = {
            'add': self.add,
            'list': self.list,
            'remove': self.remove,
            'roles': self.roles
        }.get(args[0], None)

        if command is None:
            raise Exception(
                '\nWrong Command: %s is not a valid argument' % args[0] +
                '               The valid arguments are register,'
                ' add and roles.\n'
                '               For more information type '
                '"python sdutil roles" to open the command help menu.')

        args.pop(0)
        command(args)

    def add(self, args):
        """ Process args to execute code add a user
        """
        if not args:
            self.help()
        useremail = str(args[0]).lower()

        args.pop(0)
        if not args:
            self.help()

        sdpath = str(args[0])

    
        args.pop(0)
        if not args:
            self.help()

        role = str(args[0])

        if role.upper() not in Config.USER_ROLES:
            raise Exception(
                '\nWrong Command: %s is not a valid role' % role +
                '               The valid roles are '
                '[admin, viewer].\n'
                '               For more information type '
                '"python sdutil user"'
                ' to open the command help menu.')

        print('')
        print('> Register %s as %s in the subproject %s ...'
                % (useremail, role, sdpath), end='')
        sys.stdout.flush()
        SeismicStoreService(self._auth).user_add(sdpath, useremail, role)
        print('OK')
        sys.stdout.flush()
        return

        raise Exception(
            '\n' +
            'Wrong Command: ' + sdpath +
            ' is not a valid subproject path.\n' +
            '               The valid argument is'
            ' sd://<tenant_name>/<subproject_name>.\n' +
            '               For more information type "python sdutil user"'
            ' to open the command help menu.')

    def list(self, args):
        if not args:
            self.help()

        sdpath = args[0]
        args.pop(0)

        if not Utils.isSubProject(sdpath):
            raise Exception(
                '\n' +
                'Wrong Command: ' + sdpath +
                ' is not a valid seismic store subproject path.\n' +
                '               For more information type "python sdutil user"'
                ' to open the command help menu.')

        print('')
        print('> Retriving the list of users in ' + sdpath + ' ... ', end='')
        sys.stdout.flush()
        rx = SeismicStoreService(self._auth).user_list(sdpath)
        print('OK')
        sys.stdout.flush()
        print('')
        ml = max([len(row[0]) for row in rx]) + 3
        admins = []
        for item in rx:
            if item[1] == 'admin':
                admins.append(item[0])
                print('- ' + item[0], end='')
                print(' ' * (ml - len(item[0])), end='')
                print(item[1])                
            else:
                if item[0] not in admins:
                    print('- ' + item[0], end='')
                    print(' ' * (ml - len(item[0])), end='')
                    print(item[1])

    def remove(self, args):
        if not args:
            self.help()
        useremail = str(args[0]).lower()

        args.pop(0)
        if not args:
            self.help()

        sdpath = str(args[0])

        if not Utils.isSubProject(sdpath):
            raise Exception(
                '\n' +
                'Wrong Command: ' + sdpath +
                ' is not a valid seismic store subproject path.\n' +
                '               For more information type "python sdutil user"'
                ' to open the command help menu.')

        print('')
        print('> Remove ' + useremail + ' from the subproject ' +
              sdpath + ' ... ', end='')
        sys.stdout.flush()
        SeismicStoreService(self._auth).user_remove(sdpath, useremail)
        print('OK')
        sys.stdout.flush()

    def roles(self, args):
        if not args:
            self.help()

        sdpath = args[0]
        args.pop(0)

        if not Utils.isTenant(sdpath):
            raise Exception(
                '\n' +
                'Wrong Command: ' + sdpath +
                ' is not a valid seismic store tenant path.\n' +
                '               For more information type "python sdutil user"'
                ' to open the command help menu.')

        print('> Retriving seismic store roles ...', end=' ')
        sys.stdout.flush()
        sd = SDPath(sdpath)
        rx = SeismicStoreService(self._auth).user_roles(sdpath)
        print('OK', end='\n\n')
        sys.stdout.flush()

        if sd.tenant is not None and rx['roles'] is not None:
            # Group roles by subproject
            groupedRoles = {}
            for item in rx['roles']:
                if item[0] not in groupedRoles:
                    groupedRoles[item[0]] = []
                groupedRoles[item[0]].append(item[1])

            # Determine spacing for roles alignment
            lmax = 0
            for subproject in groupedRoles:
                lmax = max(lmax, len(subproject))

            # Print out roles
            for subproject, roles in groupedRoles.items():
                #  if subproject is admin we then use max spacing
                path = sd.tenant
                spacing = lmax
                if subproject != '/admin':
                    path += subproject
                    spacing = lmax - len(subproject)

                print(' - %s %s %s' % (path, ' ' * spacing,
                                       ', '.join(roles)))
