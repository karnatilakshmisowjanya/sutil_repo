#!/usr/bin/env python
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

import sys

from sdlib.auth.auth_service import AuthFactory
from sdlib.cmd.helper import CMDHelper
from sdlib.shared.config import Config

# Ensure it is executed with python3
if sys.version_info[0] < 3:
    raise Exception("\nThe utility must be executedusing Python 3")

def main():
    try:

        if len(sys.argv) < 2:
            raise Exception(CMDHelper.main_help()[:-1])

        args = sys.argv[1:]
        cmd_name = args[0]
        positional_args, keyword_args = CMDHelper.getPosAndKeyWordArguments(args)

        if cmd_name not in CMDHelper.getCmdNames():
            raise Exception(CMDHelper.main_help()[:-1])

        Config.load()

        if cmd_name != "config":
            Config.load_user_config()

        cmd = import_from('sdlib.cmd.%s.cmd' % cmd_name.lower(),
                          cmd_name.capitalize())

        auth_provider = AuthFactory.build(Config.get_auth_provider(), keyword_args.idtoken)
        cmd(auth_provider).execute(positional_args, keyword_args)

    except Exception as ex:  # pylint: disable=W0703
        print(str(ex) + '\n')
        return 1

    print('')
    return 0


def import_from(module, name):
    module = __import__(module, fromlist=[name])
    return getattr(module, name)


if __name__ == '__main__':
    sys.exit(main())
