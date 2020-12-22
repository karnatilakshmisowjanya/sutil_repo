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
from mock import patch, Mock, mock_open, ANY

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)))))

from sdlib.cmd.cp.cmd import Cp
from sdlib.cmd.keyword_args import KeywordArguments

from test.utest import SdUtilTestCase


if sys.version[0] == "3":
    builtins = "builtins"
else:
    builtins = "__builtin__"


class TestCmdCp(SdUtilTestCase):

    @patch("sdlib.cmd.cp.cmd.SeismicStoreService")
    @patch("sdlib.cmd.cp.cmd.StorageFactory")
    @patch("sdlib.cmd.cp.cmd.Dataset")
    @patch("os.path.isfile", return_value=True)
    @patch("os.path.getsize", return_value=1)
    def test_passes_seismicmeta_to_dataset_when_passed(self, getsize, isfile,
                                                       Dataset,
                                                       StorageFactory,
                                                       SeismicStoreService):
        # set input args, keyword args
        cmd = Cp(None)
        args = ["/my/local/file", "sd://tenant/subproject/copy_to_here"]
        keyword_args = KeywordArguments()
        keyword_args.seismicmeta = "my_seismic_meta_file"

        # so we get mock object back from call creation
        SeismicStoreService.return_value = SeismicStoreService
        SeismicStoreService.dataset_register.return_value = "dummy"

        with patch("%s.open" % builtins, mock_open(read_data='{"abc": "def"}')) as mock_file:
            cmd.execute(args, keyword_args)

            # check we open the correct passed seismic meta file for opening
            mock_file.assert_called_with("my_seismic_meta_file", "r")

            # check we passed data in seismicmeta file to dataset.from_json
            # call
            SeismicStoreService.dataset_register.assert_called_with(
                ANY, ANY, ANY, {"abc": "def"})

            # dummy is output from SSS.dataset_register
            Dataset.from_json.assert_called_with("dummy")

    def test_execute(self):
        cmd = Cp(None)

        with patch('sdlib.cmd.helper.CMDHelper.cmd_help'):
            args = []
            with self.assertRaises(Exception):
                cmd.execute(args, KeywordArguments())

            args = ['sd://tnx01/spx01', 'lfile']
            with self.assertRaises(Exception):
                cmd.execute(args, KeywordArguments())

            args = ['sdx//', 'sdx//']
            with self.assertRaises(Exception):
                cmd.execute(args, KeywordArguments())