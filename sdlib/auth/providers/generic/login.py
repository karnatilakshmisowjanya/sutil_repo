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
import logging
import webbrowser
import stat

from flask import Flask, request
from six.moves import cPickle as pickle

from sdlib.shared.config import Config

_app = Flask(__name__)
_app.secret_key = '!secret'

_oauth = None
_oauth_provider = None
_credential_filename = None


def login(oauth_client, oauth_provider, oauth_rulr, credential_filename):
    global _oauth
    global _oauth_provider
    global _credential_filename

    _credential_filename = credential_filename
    _oauth = oauth_client
    _oauth.init_app(app=_app)
    _oauth_provider = _oauth.create_client(oauth_provider)    

    # NOTE: the Config.OAuth.REDIRECT_URI must match the registered URI with provider.
    rv = _oauth_provider.create_authorization_url(oauth_rulr)
    redirect_url = rv['url']

    webbrowser.open(redirect_url)
    logging.getLogger('werkzeug').setLevel(logging.ERROR)
    _app.run(port=4300)


@_app.route('/auth/callback', methods=['GET', 'POST'])
def callback():
    return callback_for_oauth()


def callback_for_oauth():
    global _oauth_provider
    token = _oauth_provider.authorize_access_token()
    # Get User Info from OpenID
    userinfo = _oauth_provider.parse_id_token(token)

    ftkdir = os.path.join(os.path.expanduser("~"), Config.HOME)
    if not os.path.isdir(ftkdir):
        os.mkdir(ftkdir)
    global _credential_filename    
    ftkfile = os.path.join(ftkdir, _credential_filename)
    with open(ftkfile, "wb") as fh:
        pickle.dump(token, fh)
    # Help prevent others from stealing the credentials.
    # CAVEAT: chmod has little effect on windows.
    os.chmod(ftkfile, stat.S_IRUSR | stat.S_IWUSR)
    shutdown_server()
    return 'User Logged in as: ' + userinfo['name'] + ' (' + userinfo['email'] + ')'


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise Exception('Not running with the Werkzeug Server')
    func()
