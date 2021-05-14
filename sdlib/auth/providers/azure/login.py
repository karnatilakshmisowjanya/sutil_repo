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
import os
import sys
import logging
import time
import requests

from authlib.integrations.flask_client import OAuth
from six.moves import cPickle as pickle

from flask import Flask, request
cli = sys.modules['flask.cli']
cli.show_server_banner = lambda *x: None

from sdlib.shared.config import Config
from .config import Oauth2Configuration

_app = Flask(__name__)
_app.secret_key = '!secret'

_oauth_client = None
_configuration = None

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise Exception('Not running with the Werkzeug Server')
    func()

def login(configuration: Oauth2Configuration):
    global _configuration

    _configuration = configuration
   
    authority_uri=_configuration.oauht2_authorize_url
    auth_obj = {
            "grant_type": _configuration.oauth2_login_grant_type,
            "client_id": _configuration.oauth2_client_id,
            "client_secret": _configuration.oauth2_client_secret,
            "refresh_token": _configuration.oauth2_refresh_token,
            "scope": _configuration.oauth2_scopes
        }

    x = requests.post(authority_uri, data = auth_obj)
        
    token = json.loads(x.text)
    token["expiration"] = int(token["expires_in"]) + time.time()

    # ensure the directory exist if not create it
    if not os.path.isdir(_configuration.token_file_dir):
        os.mkdir(_configuration.token_file_dir)

    # write the file token
    with open(_configuration.token_file, "w") as fh:
        json.dump(token, fh)

    print("Successfully logged into Azure SDUTIL.")