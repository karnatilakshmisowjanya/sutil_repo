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


from test.e2e.utils import set_args, run_command, e2e_test_dataset_01


def test_sdutil_stat_subproject(capsys, pargs):
   set_args("stat {path} --idtoken={stoken}".format(path=(pargs.sdpath), stoken=pargs.idtoken))
   status, output = run_command(capsys)
   assert not status

def test_sdutil_stat(capsys, pargs):
   set_args("stat {path} --idtoken={stoken}".format(path=(pargs.sdpath + '/' + e2e_test_dataset_01), stoken=pargs.idtoken))
   status, output = run_command(capsys)
   assert not status