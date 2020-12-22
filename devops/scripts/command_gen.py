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


from __future__ import print_function

import sys
import os
import json

if len(sys.argv) != 2:
    print('Usage: ./cmdgen <command_name_lowercase>')
    exit(1)

cmdname = sys.argv[1]

if cmdname.lower() != cmdname:
    print('Usage: ./cmdgen <command_name_lowercase>')
    exit(1)

dircmd = os.path.join(
    os.path.join(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__))), 'sdlib'), 'cmd')
regfiles = [os.path.join(x, 'reg.json') for x in
            filter(lambda x: os.path.isdir(x) and "__pycache__" not in x,
                   map(lambda x: os.path.join(dircmd, x), os.listdir(dircmd)))]
data = []
for rfile in regfiles:
    with open(rfile) as f:
        data.append(json.load(f))
commands = [x['name'] for x in data]

if cmdname in commands:
    print('The command ' + cmdname + ' has already been registered')
    exit(1)

dircmd = os.path.join(dircmd, cmdname)
os.makedirs(dircmd)

finit = os.path.join(dircmd, '__init__.py')
fcmd = os.path.join(dircmd, 'cmd.py')
freg = os.path.join(dircmd, 'reg.json')

open(finit, 'a').close()

reg = {
    "name": cmdname,
    "description": "<TODO: command_short_description> (madatory)>",
    "help": [
        "<TODO: build help menu (check reg.json in other cmd as examples)>"
    ]
}

with open(freg, 'w') as f:
    json.dump(reg, f, sort_keys=True, indent=4, ensure_ascii=False)

with open(fcmd, 'w') as f:
    f.write('''from __future__ import print_function

import os

from sdlib.cmd.cmd import SDUtilCMD
from sdlib.cmd.helper import CMDHelper


class ''' + cmdname.capitalize() + '''(SDUtilCMD):

    def __init__(self, auth):
        self._auth = auth

    @staticmethod
    def help():
        CMDHelper.cmd_help(
            os.path.join(
                os.path.dirname(
                    os.path.abspath(__file__)), 'reg.json'))

    def execute(self, args, keyword_args):
        print('TODO: Not Implemented Yet')
''')
