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

import yaml


class Config(object):

    HOME = ".sdcfg"
    CONFIG_FILE = "sducfg.json"
    SDPATH_PREFIX = 'sd://'
    USER_ROLES = ['ADMIN', 'VIEWER']

    __configuration = {}
    __user_configuration = {}


    @classmethod 
    def load(cls, forced_configuration=None):
        '''
        # The main configuration (config.yaml) should match this schema
        seistore:
            service: "service configurations as stringify JSON"
        auth_provider:
            "auth_provider_name": "auth provider configurations as stringify JSON"
        read_only_file_formats:
            "read_only_file_formats": "file formats which are considered as readonly for all upload operations "
        '''

        cls.__configuration = forced_configuration
        if not cls.__configuration:
            configuration_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', "config.yaml")
            if os.path.exists(configuration_file):
                with open(configuration_file, 'r') as fh:
                    cls.__configuration = yaml.load(fh, Loader=yaml.FullLoader)
            else:
                raise Exception("\nThe \"sdlib/config.yaml\" utility configuration has not been found."); 

        assert "seistore" in cls.__configuration, "\n- configuration \"seistore\" not found in config.yaml"
        assert "service" in cls.__configuration["seistore"], "\n- configuration \"seistore:service\" not found in config.yaml"
        assert "auth_provider" in cls.__configuration, "\n- configuration \"auth_provider\" not found in config.yaml"

        # check if the auth provider configuration is set
        if len(list(cls.__configuration['auth_provider'].keys())) != 1:
            raise Exception("\nThe \"sdlib/config.yaml\" utility configuration is invald."); 
        
        # check if the auth provider implement exist
        auth_provider_name = list(cls.__configuration['auth_provider'].keys())[0]
        if not os.path.isdir(os.path.join(*[os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "auth", "providers", auth_provider_name])):
            raise Exception("\nThe \""+auth_provider_name+"\" implementation has not been found."); 

        # load auth provider configurations as json
        cls.__configuration['seistore']['service'] = json.loads(cls.__configuration['seistore']['service'])
        auth_config = cls.__configuration['auth_provider'][auth_provider_name]
        if auth_config != '#{config.auth_provider.default}#' and auth_config != None and len(auth_config) > 0 :
            cls.__configuration['auth_provider'][auth_provider_name] = json.loads(cls.__configuration['auth_provider'][auth_provider_name])

        # load default readonly file formats 
        if  cls.__configuration.get('read_only_file_formats', False):
            cls.__configuration['read_only_file_formats'] = json.loads(cls.__configuration['read_only_file_formats'])
        
    @classmethod
    def load_user_config(cls,  forced_configuration=None):
        ''' Load configuration'''

        configuration = forced_configuration
        if not configuration:
            configuration_file = os.path.join(os.path.expanduser("~"), cls.HOME, cls.CONFIG_FILE)
            if os.path.exists(path=configuration_file):
                with open(configuration_file, "r") as fh:
                    configuration = json.load(fh)
            else:
                raise Exception("\nUtility configuration not found. Please run \"sdutil config init\" to initialize the utitlity")

        config_service = cls.__configuration['seistore']['service']
        if 'cloudprovider' not in configuration:
            raise Exception("\nUtility configuration invalid. Please run \"sdutil config init\" to re-initialize the utility")
        if configuration["cloudprovider"] not in config_service:
            raise Exception("\nUtility configuration invalid. Please run \"sdutil config init\" to re-initialize the utility")
        cls.__user_configuration["cloudprovider"] = configuration["cloudprovider"]

        if 'env' not in configuration:
            raise Exception("\nUtility configuration invalid. Please run \"sdutil config init\" to re-initialize the utility")
        if configuration["env"] not in config_service[cls.__user_configuration["cloudprovider"]]:
            raise Exception("\nUtility configuration invalid. Please run \"sdutil config init\" to re-initialize the utility")
        cls.__user_configuration["env"] = configuration["env"]


        if 'url' not in config_service[cls.__user_configuration["cloudprovider"]][cls.__user_configuration["env"]]:
            raise Exception("\nUtility configuration invalid. Please run \"sdutil config init\" to re-initialize the utility")
        cls.__user_configuration["url"] = config_service[cls.__user_configuration["cloudprovider"]][cls.__user_configuration["env"]]['url']

        if 'appkey' in configuration:
            cls.__user_configuration["appkey"] = configuration['appkey']
        else:
            cls.__user_configuration["appkey"] = ''

        if "appkey_header_name" in config_service[cls.__user_configuration["cloudprovider"]][cls.__user_configuration["env"]]:
            cls.__user_configuration["appkey_name"] = config_service[cls.__user_configuration["cloudprovider"]][cls.__user_configuration["env"]]['appkey_header_name']
        else:
            cls.__user_configuration["appkey_name"] = 'appkey'
        
        if "ssl_verify" in config_service[cls.__user_configuration["cloudprovider"]][cls.__user_configuration["env"]]:
            cls.__user_configuration["verify_ssl"] = config_service[cls.__user_configuration["cloudprovider"]][cls.__user_configuration["env"]]['ssl_verify']
        else:
            cls.__user_configuration["verify_ssl"] = True

        if cls.__user_configuration["verify_ssl"] == False:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        if "sdms_target_audience" in config_service[cls.__user_configuration["cloudprovider"]][cls.__user_configuration["env"]]:
            cls.__user_configuration["sdms_target_audience"] = config_service[cls.__user_configuration["cloudprovider"]][cls.__user_configuration["env"]]['sdms_target_audience']
        
        if "de_target_audience" in config_service[cls.__user_configuration["cloudprovider"]][cls.__user_configuration["env"]]:
            cls.__user_configuration["de_target_audience"] = config_service[cls.__user_configuration["cloudprovider"]][cls.__user_configuration["env"]]['de_target_audience']

    @classmethod
    def get_auth_provider_configurations(cls):
        return cls.__configuration['auth_provider'][list(cls.__configuration['auth_provider'].keys())[0]]

    @classmethod
    def get_service_configurations(cls):
        return cls.__configuration['seistore']['service']

    @classmethod
    def get_cloud_provider(cls):
        # pylint: disable=no-member
        return cls.__user_configuration["cloudprovider"]

    @classmethod
    def get_svc_env(cls):
        # pylint: disable=no-member
        return cls.__user_configuration["env"]

    @classmethod
    def get_svc_url(cls):
        # pylint: disable=no-member
        return cls.__user_configuration["url"]

    @classmethod
    def get_svc_appkey(cls):
        # pylint: disable=no-member
        return cls.__user_configuration["appkey"]

    @classmethod
    def get_svc_appkey_name(cls):
        # pylint: disable=no-member
        return cls.__user_configuration["appkey_name"]

    @classmethod
    def get_ssl_verify(cls):
        # pylint: disable=no-member
        return cls.__user_configuration["verify_ssl"]

    @classmethod
    def get_svc_target_audiences(cls):
        aud = ''
        if 'sdms_target_audience' in cls.__user_configuration:
            aud += cls.__user_configuration['sdms_target_audience']
        if 'de_target_audience' in cls.__user_configuration:
            if(len(aud) > 0):
                aud += ' '
            aud += cls.__user_configuration['de_target_audience']
        return aud

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
        return list(cls.__configuration['auth_provider'].keys())[0]


    @classmethod
    def get_readonly_file_formats(cls):
        return cls.__configuration.get('read_only_file_formats', [])
