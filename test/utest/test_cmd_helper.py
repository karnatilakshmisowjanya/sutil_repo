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
import os
import unittest

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                    os.path.abspath(__file__)))))

from sdlib.cmd.helper import CMDHelper


class TestCmdHelper(unittest.TestCase):

    def test_helper(self):

        CMDHelper.getRegFiles()
        CMDHelper.getMainHelp()
        CMDHelper.getCmdNames()
        CMDHelper.main_help()
        with self.assertRaises(SystemExit):
            CMDHelper.cmd_help(
                os.path.join(os.path.join(os.path.join(os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                'sdlib'), 'cmd'), 'stat'), 'reg.json'))
        CMDHelper.cmd_help(
            os.path.join(os.path.join(os.path.join(os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            'sdlib'), 'cmd'), 'version'), 'reg.json'))

    def test_getPosAndKeyWordArguments_returns_correct_positional(self):

        args = ["sdutil.py", "abc", "--idtoken=mytoken"]
        pos_args, kw_args = CMDHelper.getPosAndKeyWordArguments(args)

        self.assertEqual(pos_args, ["abc"])

    def test_getPosAndKeyWordArguments_returns_object_with_correct_values(self):

        args = ["abc", "--idtoken=mytoken"]
        pos_args, kw_args = CMDHelper.getPosAndKeyWordArguments(args)

        self.assertEqual(kw_args.idtoken, "mytoken")

    def test_getPosAndKeyWordArguments_returns_object_with_none_for_missing_tokens(self):

        args = ["abc", "other", "args"]
        pos_args, kw_args = CMDHelper.getPosAndKeyWordArguments(args)

        self.assertEqual(kw_args.random, None)

    def test_getPosAndKeyWordArguments_trims_quotes(self):

        args = ["abc", '--idtoken="mytoken"']
        pos_args, kw_args = CMDHelper.getPosAndKeyWordArguments(args)

        self.assertEqual(kw_args.idtoken, "mytoken")

    def test_getPosAndKeyWordArguments_trims_quotes(self):

        args = ["abc", "--idtoken='mytoken'"]
        pos_args, kw_args = CMDHelper.getPosAndKeyWordArguments(args)

        self.assertEqual(kw_args.idtoken, "mytoken")

    def test_getPosAndKeyWordArguments_flag_argument(self):

        args = ["abc", "--detailed", "-d"]
        pos_args, kw_args = CMDHelper.getPosAndKeyWordArguments(args)

        self.assertEqual(kw_args.d, True)
        self.assertEqual(kw_args.detailed, True)

    def test_getPosAndKeyWordArguments_flag_with_dash(self):

        args = ["abc", "--full-path"]
        pos_args, kw_args = CMDHelper.getPosAndKeyWordArguments(args)

        self.assertEqual(kw_args.full_path, True)