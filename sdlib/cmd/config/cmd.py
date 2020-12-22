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
import json

from sdlib.cmd.cmd import SDUtilCMD
from sdlib.cmd.helper import CMDHelper
from sdlib.shared.config import Config as Configuration

from six.moves import input


class Config(SDUtilCMD):

    def __init__(self, auth):
        self._auth = auth
        self._form = "\nAvailable configurations:\n\n"

    @staticmethod
    def help():
        reg = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reg.json')
        CMDHelper.cmd_help(reg)

    def execute(self, args, keyword_args):

        if not args:
            self.help()

        command = {
            'init': self.init,
            'show': self.show
        }.get(args[0], None)

        if command is None:
            raise Exception(
                '\nWrong Command: %s is not a valid argument' % args[0] +
                '. The valid arguments are init and show.' +
                '\n               For more information type ' +
                '"python sdutil config" to open the command help menu.')

        args.pop(0)
        command(args)

    def init(self, args):

        # set the cloud provider
        idx_to_env = {str(idx+1): env
                      for idx, env in enumerate(Configuration.SEISTORE.SERVICE.keys())}
        print()
        for idx, env in enumerate(Configuration.SEISTORE.SERVICE.keys()):
            print("[" + str(idx + 1) + "] " + env)
        print("\nSelect the cloud provider: ", end='')
        sys.stdout.flush()
        idx = sys.stdin.readline()
        try:
            idx = int(idx)
        except Exception:
            raise Exception("\nInvalid choice.")
        if idx < 1 or idx > len(Configuration.SEISTORE.SERVICE.keys()):
            raise Exception("\nInvalid choice.")
        provider = idx_to_env[str(idx)]
        provider_envs = Configuration.SEISTORE.SERVICE[provider]

        # set the deployemnt environemnt
        idx_to_env = {str(idx+1): env
                      for idx, env in enumerate(provider_envs)}
        if len(idx_to_env) > 1:
            print()
            for idx, env in enumerate(provider_envs):
                print("[" + str(idx + 1) + "] " + env)
            print("\nSelect the " + provider + " deployment: ", end='')
            sys.stdout.flush()
            idx = sys.stdin.readline()
            try:
                idx = int(idx)
            except Exception:
                raise Exception("\nInvalid choice.")
            if idx < 1 or idx > len(provider_envs):
                raise Exception("\nInvalid choice.")
        else:
            idx = 1
        provider_env = idx_to_env[str(idx)]
        provider_config = provider_envs[provider_env]

        # set the deployemnt appkey if required (optional)
        appkey = None 
        if 'appkey' in provider_config:
            if len(provider_config['appkey']) == 0:
                print("\nInsert the " + provider + " (" + provider_env + ")" +  " application key: ", end='')
                sys.stdout.flush()
                appkey = sys.stdin.readline().rstrip()
            else:
                appkey = provider_config['appkey']

        # save the configuration
        print("\nsdutil successfully configured to use " + provider + " (" + provider_env + ")")
        Configuration.save_config(provider, provider_env, appkey)

    def show(self, args):
        Configuration.load_config()
        print()
        print('Provider    : ' + Configuration.get_cloud_provider())
        print('Service Url : ' + Configuration.get_svc_url())
        if Configuration.get_svc_appkey():
            print('Serivce Key : ' + Configuration.get_svc_appkey())
        print('Serivce Env : ' + Configuration.get_svc_env())