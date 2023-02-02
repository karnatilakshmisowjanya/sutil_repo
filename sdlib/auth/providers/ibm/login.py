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
import webbrowser
import stat

from authlib.integrations.flask_client import OAuth
from authlib.integrations.requests_client import OAuth2Session

from flask import Flask, request
cli = sys.modules['flask.cli']
cli.show_server_banner = lambda *x: None

from sdlib.shared.config import Config
from .config import Oauth2Configuration

_app = Flask(__name__)
_app.secret_key = '!secret'

_oauth_client = None
_configuration = None

@_app.route('/auth/callback', methods=['GET', 'POST'])
def callback():

    shutdown_server()

    global _configuration
    global _oauth_client

    oauth_state = request.args.get('state')
    myclient = OAuth2Session(_configuration.oauth2_client_id, _configuration.oauth2_client_secret, state=oauth_state, redirect_uri=_configuration.oauth2_client_redirect_url)
    token = myclient.fetch_token(_configuration.oauht2_access_token_url, authorization_response=request.url)

    #token = _oauth_client.authorize_access_token()
    userinfo = _oauth_client.parse_id_token(token)

    # ensure the directory exist if not create it
    if not os.path.isdir(_configuration.token_file_dir):
        os.mkdir(_configuration.token_file_dir)

    # write the file token
    with open(_configuration.token_file, "w") as fh:
        json.dump(token, fh)

    # Help prevent others from stealing the credentials. CAVEAT: chmod has little effect on windows.
    os.chmod(_configuration.token_file, stat.S_IRUSR | stat.S_IWUSR)

    return 'User Logged in as: ' + userinfo['name'] + ' (' + userinfo['email'] + ')'


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise Exception('Not running with the Werkzeug Server')
    func()

def login(configuration: Oauth2Configuration):


    global _configuration
    global _oauth_client

    _configuration = configuration

    oauth_client = OAuth()
    oauth_client.register(
        name=_configuration.oauht2_provider,
        client_id=_configuration.oauth2_client_id,
        client_secret=_configuration.oauth2_client_secret,
        authorize_url=_configuration.oauht2_authorize_url,
        authorize_params=_configuration.oauht2_authorize_params,
        refresh_token_url=_configuration.oauht2_refresh_token_url,
        refresh_token_params=_configuration.oauht2_refresh_token_param,
        access_token_url=_configuration.oauht2_access_token_url,
        access_token_params=_configuration.oauht2_access_token_params,
        client_kwargs={"scope": _configuration.oauht2_scope},
        server_metadata_url=_configuration.oauht2_open_id_url)
    oauth_client.init_app(app=_app)
    _oauth_client = oauth_client.create_client(_configuration.oauht2_provider)    

    # NOTE: the Config.OAuth.REDIRECT_URI must match the registered URI with provider.
    redirect_url = _oauth_client.create_authorization_url(_configuration.oauth2_client_redirect_url)['url']

    webbrowser.open(redirect_url)
    logging.getLogger('werkzeug').setLevel(logging.ERROR)
    _app.run(port=_configuration.oauth2_client_redirect_url_port)

