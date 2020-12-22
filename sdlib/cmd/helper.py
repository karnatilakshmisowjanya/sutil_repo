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


import os
import json
from sdlib.cmd.keyword_args import KeywordArguments


class CMDHelper(object):

    @staticmethod
    def getRegFiles():
        dircmd = os.path.dirname(__file__)
        full_cmd_dirs = map(lambda x: os.path.join(dircmd, x),
                            os.listdir(dircmd))
        return [os.path.join(x, 'reg.json')
                for x in filter(lambda x: os.path.isdir(x) and "__pycache__" not in x,
                                full_cmd_dirs)]

    @staticmethod
    def getMainHelp():
        data = []
        for rfile in CMDHelper.getRegFiles():
            with open(rfile) as f:
                data.append(json.load(f))
        names = [x['name'] for x in data]
        descriptions = [x['description'] for x in data]
        return names, descriptions

    @staticmethod
    def getVersion():
        version = " "
        if os.path.isfile('.version'):
            with open('.version', 'r') as fx:
                version = " " + fx.read() + " "
        return version

    @staticmethod
    def getCmdNames():
        data = []
        for rfile in CMDHelper.getRegFiles():
            with open(rfile) as f:
                data.append(json.load(f))
        return [x['name'] for x in data]

    @staticmethod
    def getPosAndKeyWordArguments(args):
        """ This will capture any keyword arguments like
        --XXX=YYY and remove these from positional arguments list
        Parameters:
            args (list) - The list of arguments
        Returns:
            position_args (list) - list of all non keyword args,
                                    e.g. all positional
            kw_args (KeywordArguments) - object that has any keyword
                            arguments as attributes.
                            Note: missing attributes will have a value of None
                            e.g.
                            kw_args.idtoken will be None or value of
                            --idtoken=YYY
        """
        kw_args = KeywordArguments()
        positional_args = args[1:]

        for arg in list(args):
            if arg.startswith("-"):
                if arg.startswith("--") and "=" in arg:
                    # capture any arguments like --XXX=YYY
                    parts = arg.split("=")
                    name = parts[0].strip("-")
                    value = "=".join(parts[1:])
                    value = value.strip('"')
                    value = value.strip("'")
                    name = name.replace("-", "_")
                    setattr(kw_args, name, value)
                else:
                    name = arg.strip("-")
                    name = name.replace("-", "_")
                    setattr(kw_args, name, True)
                positional_args.remove(arg)

        return positional_args, kw_args

    @staticmethod
    def main_help():
        version = CMDHelper.getVersion().replace(" ", "")
        if len(version) > 0:
            version = ' (' + version + ')'
        names, descriptions = CMDHelper.getMainHelp()
        lmax = max([len(x) for x in names])
        s = '\nSeismic Store Utility' + version + '\n\n'
        s += '> python sdutil [command]\n\n'
        s += 'available commands:\n\n'
        for name, desc in zip(names, descriptions):
            spacing = ' ' * (lmax - len(name))
            s += ' * ' + name + spacing + ' : ' + desc + '\n'
        return s

    @staticmethod
    def cmd_help(helpfile):
        with open(helpfile) as f:
            reg = json.load(f)
            version = CMDHelper.getVersion().replace(" ", "")
            if len(version) > 0:
                version = ' (' + version + ')'
            if 'help' in reg:
                # s = '\n---------------------------------------------------\n'
                s = '\nSeismic Store Utility' + version + '\n'
                # s += '---------------------------------------------------\n'
                s += '\ncommand name: ' + reg['name']
                s += '\ncommand desc: ' + reg['description'] + '\n\n'
                # s += '\n---------------------------------------------------\n\n'  # noqa E501
                s += '\n'.join(reg['help']) + '\n'
                # s += '\n\n---------------------------------------------------'
                print(s)
                exit(0)
