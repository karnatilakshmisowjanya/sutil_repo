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

import yaml
import os
import json

from sdlib.shared.config import Config

_yaml_file = os.path.abspath(
    os.path.join(
        os.path.join(
            os.path.join(
                os.path.join(
                    os.path.dirname(os.path.abspath(__file__)), os.pardir), os.pardir), "sdlib"), "config.yaml"))

with open(_yaml_file, 'r') as fh:
    _config_spec = yaml.load(fh, Loader=yaml.FullLoader)

configuration = json.loads(_config_spec['seistore']['service'])

provider = list(configuration.keys())[0]
env = list(configuration[provider].keys())[0]
appkey = None
if 'appkey' in configuration[provider][env]:
    appkey = configuration[provider][env]['appkey']

Config.save_config(provider, env, appkey)

os.environ["OAUTH2_CLIENT_ID"] = "test"
os.environ["OAUTH2_CLIENT_SECRET"] = "test"
os.environ["OAUTH2_CLIENT_REDIRECT_URL"] = "https://test/auth/callback"
