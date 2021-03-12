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

import json
import base64

from test.e2e.utils import run_command, check_string, set_args


def test_sdutil_user_add(capsys, pargs):
   temp = pargs.sdpath.split("/")
   tsp_path = "/".join(["sd:/", temp[2], temp[3]])
   payload = pargs.idtoken.split('.')[1]
   missing_padding = len(payload) % 4
   if missing_padding != 0:
      payload += '=' * (4 - missing_padding)
   email = json.loads(base64.b64decode(payload)).get('email') or json.loads(base64.b64decode(payload))['username']
   set_args("user add {email} {path} viewer --idtoken={stoken}".format(path=tsp_path, stoken=pargs.idtoken, email=email))
   status, output = run_command(capsys)
   assert not status
   assert check_string(output, "OK")
