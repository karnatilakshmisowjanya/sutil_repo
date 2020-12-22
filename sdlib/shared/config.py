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


import fnmatch
import json
import os
import sys

import yaml


class Value(object):
    pass


def dfs_setattr(config, yaml_spec):
    """
    Set attribute on an object

    :param config:
    :param yaml_spec:
    :return:
    """
    for key, value in yaml_spec.items():
        if isinstance(value, dict):
            value_set = Value()
            setattr(config, key.upper(), value_set)
            dfs_setattr(value_set, value)
        else:
            setattr(config, key.upper(), value)
    return config


def validate_schema(config_spec):

    # required configurations

    # Default Auth Provider
    assert "auth_provider" in config_spec, "\n- configuration \"auth_provider\" not found in config.yaml"
    assert "default" in config_spec[
        "auth_provider"], "\n- configuration \"auth_provider:default\" not found in config.yaml"

    # Seistore
    assert "seistore" in config_spec, "\n- configuration \"seistore\" not found  in config.yaml"
    assert "service" in config_spec["seistore"], "\n- configuration \"seistore:service\" not found in config.yaml"


class Config(object):
    HOME = ".sdcfg"
    CONFIG_FILE = "sducfg.json"
    SDPATH_PREFIX = 'sd://'
    USER_ROLES = ['ADMIN', 'EDITOR', 'VIEWER']

    _yaml_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', "config.yaml")

    @classmethod
    def parse_config_yamls(cls):
        # pylint: disable=no-member

        # list all configurations files
        config_file_names = fnmatch.filter(
            os.listdir(
                os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')), 'config*.yaml')

        # main configuration required
        if 'config.yaml' not in config_file_names:
            raise Exception(
                '\nMain configuration file \"config.yaml\" not found!')

        # load main configuration
        with open(cls._yaml_file, 'r') as fh:
            _config_spec = yaml.load(fh, Loader=yaml.FullLoader)
            validate_schema(_config_spec)

        # remove from list as already loaded
        config_file_names.remove('config.yaml')

        # for each configuration load and ensure don't contain duplicated key
        for config_file_name in config_file_names:
            config_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', config_file_name)
            with open(config_file_path, 'r') as fh:
                custom_config_spec = yaml.load(fh, Loader=yaml.FullLoader)
            for spec in custom_config_spec:
                if spec in _config_spec:
                    raise Exception(
                        '\nDuplicated configuration \"' + spec + 
                        '\" found in ' + config_file_name)
            _config_spec.update(custom_config_spec)

        # chec if configuration is provided for the default auth provider
        if _config_spec['auth_provider']['default'] not in _config_spec:
            raise Exception(
                '\nThe \"' + _config_spec['auth_provider']['default'] 
                + '\" auth provider configuration has not been found!')

        # set attributes
        dfs_setattr(cls, _config_spec)

        # parse seistore service params into a json
        cls.SEISTORE.SERVICE = json.loads(cls.SEISTORE.SERVICE)

    @classmethod
    def load_config(cls, configuration=None):
        ''' Load configuration'''

        sd_config = configuration
        if not sd_config:
            path = os.path.join(os.path.expanduser("~"), cls.HOME, cls.CONFIG_FILE)
            if os.path.exists(path=path):
                with open(path, "r") as fh:
                    sd_config = json.load(fh)
            else:
                raise Exception("\nUtility configuration not found. Please run \"sdutil init\" to initialize the utitlity")

        if 'cloudprovider' not in sd_config:
            raise Exception("\nUtility configuration invalid. Please run \"sdutil init\" to re-initialize the utility")
        if sd_config["cloudprovider"] not in cls.SEISTORE.SERVICE:
            raise Exception("\nUtility configuration invalid. Please run \"sdutil init\" to re-initialize the utility")
        cls.SEISTORE.CLOUD_PROVIDER = sd_config["cloudprovider"]

        if 'env' not in sd_config:
            raise Exception("\nUtility configuration invalid. Please run \"sdutil init\" to re-initialize the utility")
        if sd_config["env"] not in cls.SEISTORE.SERVICE[cls.SEISTORE.CLOUD_PROVIDER]:
            raise Exception("\nUtility configuration invalid. Please run \"sdutil init\" to re-initialize the utility")
        cls.SEISTORE.ENV = sd_config["env"]

        if 'url' not in cls.SEISTORE.SERVICE[cls.SEISTORE.CLOUD_PROVIDER][cls.SEISTORE.ENV]:
            raise Exception("\nUtility configuration invalid. Please run \"sdutil init\" to re-initialize the utility")
        cls.SEISTORE.URL = cls.SEISTORE.SERVICE[cls.SEISTORE.CLOUD_PROVIDER][cls.SEISTORE.ENV]['url']

        if 'appkey' in sd_config:
            cls.SEISTORE.APPKEY = sd_config['appkey']
        else:
            cls.SEISTORE.APPKEY = ''

        if "appkey_header_name" in cls.SEISTORE.SERVICE[cls.SEISTORE.CLOUD_PROVIDER][cls.SEISTORE.ENV]:
            cls.SEISTORE.APPKEY_NAME = cls.SEISTORE.SERVICE[cls.SEISTORE.CLOUD_PROVIDER][cls.SEISTORE.ENV]['appkey_header_name']
        else:
            cls.SEISTORE.APPKEY_NAME = 'appkey'

        if "ssl_verify" in cls.SEISTORE.SERVICE[cls.SEISTORE.CLOUD_PROVIDER][cls.SEISTORE.ENV]:
            cls.SEISTORE.VERIFY_SSL = cls.SEISTORE.SERVICE[cls.SEISTORE.CLOUD_PROVIDER][cls.SEISTORE.ENV]['ssl_verify']
        else:
            cls.SEISTORE.VERIFY_SSL = True
        
        if cls.SEISTORE.VERIFY_SSL == False:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                

    @classmethod
    def get_ssl_verify(cls):
        # pylint: disable=no-member
        return cls.SEISTORE.VERIFY_SSL

    @classmethod
    def get_svc_env(cls):
        # pylint: disable=no-member
        return cls.SEISTORE.ENV

    @classmethod
    def get_svc_appkey(cls):
        # pylint: disable=no-member
        return cls.SEISTORE.APPKEY

    @classmethod
    def get_svc_url(cls):
        # pylint: disable=no-member
        return cls.SEISTORE.URL

    @classmethod
    def get_cloud_provider(cls):
        # pylint: disable=no-member
        return cls.SEISTORE.CLOUD_PROVIDER

    @classmethod
    def get_svc_appkey_name(cls):
        # pylint: disable=no-member
        return cls.SEISTORE.APPKEY_NAME

    @staticmethod
    def save_config(provider, env, appkey):

        sd_config = {
            "env": env,
            "appkey": appkey,
            "cloudprovider": provider
        }        

        file_config_dir = os.path.join(os.path.expanduser("~"), Config.HOME)
        if not os.path.exists(path=file_config_dir):
            os.makedirs(file_config_dir)

        file_config = os.path.join(file_config_dir, Config.CONFIG_FILE)
        with open(file_config, "w") as fh:
            json.dump(sd_config, fh)

    @classmethod
    def get_auth_provider(cls):
        # pylint: disable=no-member
        return cls.AUTH_PROVIDER.DEFAULT
