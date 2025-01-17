# -*- coding: utf-8 -*-
# Copyright 2017-2024, Schlumberger
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
import time
import re

import requests
from sdlib.shared.config import Config
from sdlib.shared.sdpath import SDPath
from urllib.parse import quote


class SeismicStoreService(object):

    def __init__(self, auth):
        self._auth = auth
        self._storage_access_token = None
        self._storage_exp_time = time.time() - 3600

    def get_cloud_provider(self, sdpath):
        return Config.get_cloud_provider()


    def status(self):
        url = Config.get_svc_url() + '/svcstatus'
        header = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + self._auth.get_id_token(),
            Config.get_svc_appkey_name(): Config.get_svc_appkey(),
        }
        self.update_header_if_data_partition_id_provided(header)

        resp = requests.get(url=url, headers=header,verify=Config.get_ssl_verify())
        if resp.status_code != 200:
            raise Exception('\n[' + str(resp.status_code) + '] ' + resp.text)

        return resp.text, resp.headers

    def create_subproject(self, tenant, subproject, owner_email, gcsclass,
                          gcsloc, legal_tag, access_policy, admins = None, viewers = None):

        url = Config.get_svc_url() + '/subproject/tenant/' + \
            tenant + '/subproject/' + subproject
        header = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + self._auth.get_id_token(),
            Config.get_svc_appkey_name(): Config.get_svc_appkey(),
            'ltag': legal_tag,
            'access-policy': access_policy
        }
        self.update_header_if_data_partition_id_provided(header)

        if gcsclass is not None and gcsloc is not None:
            body = {
                'admin': owner_email,
                'storage_class': gcsclass,
                'storage_location': gcsloc
            }
        else:
            body = {
                'admin': owner_email
            }

        if access_policy:
            body["access_policy"] = access_policy

        body['acls'] = {
            'admins': [] if admins is None else [admins],
            'viewers': [] if viewers is None else [viewers]
        }
        
        resp = requests.post(url=url, json=body, headers=header, verify=Config.get_ssl_verify())

        if resp.status_code != 200:
            raise Exception('\n[' + str(resp.status_code) + '] ' + resp.text)

    def get_tenant(self, tenant):

        url = Config.get_svc_url() + '/tenant/' + tenant
        header = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + self._auth.get_id_token(),
            Config.get_svc_appkey_name(): Config.get_svc_appkey(),
        }
        self.update_header_if_data_partition_id_provided(header)

        resp = requests.get(url=url, headers=header,verify=Config.get_ssl_verify())
        if resp.status_code != 200:
            raise Exception('\n[' + str(resp.status_code) + '] ' + resp.text)

        return resp.json()

    def get_subproject(self, tenant, subproject):

        url = Config.get_svc_url() + '/subproject/tenant/' + \
            tenant + '/subproject/' + subproject
        header = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + self._auth.get_id_token(),
            Config.get_svc_appkey_name(): Config.get_svc_appkey()
        }
        self.update_header_if_data_partition_id_provided(header)

        resp = requests.get(url=url, headers=header,verify=Config.get_ssl_verify())
        if resp.status_code != 200:
            raise Exception('\n[' + str(resp.status_code) + '] ' + resp.text)

        return resp.json()

    def patch_subproject(self, sdpath, legal_tag, recursive = None, access_policy = None, admins = None, viewers = None):

        body = None

        sdpath = SDPath(sdpath)

        url = Config.get_svc_url() + '/subproject/tenant/' + \
            sdpath.tenant + '/subproject/' + sdpath.subproject
        header = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + self._auth.get_id_token(),
            Config.get_svc_appkey_name(): Config.get_svc_appkey(),
            'ltag': legal_tag
        }
        self.update_header_if_data_partition_id_provided(header)

        querystring = {"recursive": "true" if recursive is not None else "false"}

        if access_policy:
            body = {
                "access_policy": access_policy
            }
        
        if admins is not None or viewers is not None:
            if body is None:
                body = {}
            body['acls'] = {
                'admins': [admins] if admins is not None else [],
                'viewers': [viewers] if viewers is not None else []
            }
            
        resp = requests.patch(url=url, headers=header, json=body, params=querystring,verify=Config.get_ssl_verify())

        if resp.status_code != 200:
            raise Exception('\n[' + str(resp.status_code) + '] ' + resp.text)

        return resp.json()

    def delete_subproject(self, tenant, subproject):

        url = Config.get_svc_url() + '/subproject/tenant/' + \
            tenant + '/subproject/' + subproject
        header = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + self._auth.get_id_token(),
            Config.get_svc_appkey_name(): Config.get_svc_appkey(),
        }
        self.update_header_if_data_partition_id_provided(header)

        resp = requests.delete(url=url, headers=header, verify=Config.get_ssl_verify())
        if resp.status_code != 200:
            raise Exception('\n[' + str(resp.status_code) + '] ' + resp.text)

    def ls(self, sdpath, limit=None, next_page_cursor=None, working_mode=None):

        url = (Config.get_svc_url()
               + '/utility/ls?sdpath='
               + quote(sdpath, safe=''))

        if limit is not None:
            url = url + '&limit=' + str(limit)
        if next_page_cursor is not None:
            url = url + '&cursor=' + quote(next_page_cursor, safe='')
        if working_mode is not None:
            url = url + '&wmode=' + working_mode

        header = {
            'Authorization': 'Bearer ' + self._auth.get_id_token(),
            Config.get_svc_appkey_name(): Config.get_svc_appkey()
        }
        self.update_header_if_data_partition_id_provided(header)

        resp = requests.get(url=url, headers=header,verify=Config.get_ssl_verify())

        if resp.status_code != 200:
            raise Exception('\n[' + str(resp.status_code) + '] ' + resp.text)

        return resp.json()

    def dataset_cp(self, sdpath_from, sdpath_to, lock=True):
        url = Config.get_svc_url() + '/utility/cp'
        querystring = {"sdpath_from": sdpath_from, "sdpath_to": sdpath_to, "lock": lock}
        header = {
            'Authorization': 'Bearer ' + self._auth.get_id_token(),
            Config.get_svc_appkey_name(): Config.get_svc_appkey()
        }
        self.update_header_if_data_partition_id_provided(header)

        resp = requests.post(url=url, headers=header, params=querystring,verify=Config.get_ssl_verify())
        
        if resp.status_code == 202 or resp.status_code == 200:
            print(resp.json())
        else:
            raise Exception('\n[' + str(resp.status_code) + '] ' + resp.text)

    def dataset_register(self, sdpath, sdtype=None, legal_tag=None,
                         seismicmeta=None):

        sdpath = SDPath(sdpath)
        url = (Config.get_svc_url()
               + '/dataset/tenant/'
               + sdpath.tenant
               + '/subproject/'
               + sdpath.subproject
               + '/dataset/'
               + sdpath.dataset)
        querystring = {"path": sdpath.path}
        header = {
            'Authorization': 'Bearer ' + self._auth.get_id_token(),
            Config.get_svc_appkey_name(): Config.get_svc_appkey(),
            'ltag': legal_tag,
        }
        self.update_header_if_data_partition_id_provided(header)

        body = {}
        body_none = True
        if sdtype is not None:
            body_none = False
            body["type"] = sdtype
        if seismicmeta is not None:
            body_none = False
            body["seismicmeta"] = seismicmeta
        if body_none:
            body = None

        resp = requests.post(url=url, headers=header,
                             json=body, params=querystring,verify=Config.get_ssl_verify())

        if resp.status_code != 200:
            raise Exception('\n[' + str(resp.status_code) + '] ' + resp.text)

        return resp.json()

    def dataset_get(self, sdpath, seismicmeta=None):

        sdpath = SDPath(sdpath)
        url = (Config.get_svc_url()
               + '/dataset/tenant/'
               + sdpath.tenant
               + '/subproject/'
               + sdpath.subproject
               + '/dataset/'
               + sdpath.dataset)

        querystring = {"path": sdpath.path, "seismicmeta": seismicmeta}
        header = {
            'Authorization': 'Bearer ' + self._auth.get_id_token(),
            Config.get_svc_appkey_name(): Config.get_svc_appkey()
        }
        self.update_header_if_data_partition_id_provided(header)

        resp = requests.get(url=url, headers=header, params=querystring,verify=Config.get_ssl_verify())

        if resp.status_code != 200:
            raise Exception('\n[' + str(resp.status_code) + '] ' + resp.text)

        return resp.json()

    def dataset_lock(self, sdpath, openmode):

        sdpath = SDPath(sdpath)
        url = (Config.get_svc_url()
               + '/dataset/tenant/'
               + sdpath.tenant
               + '/subproject/'
               + sdpath.subproject
               + '/dataset/'
               + sdpath.dataset
               + '/lock')

        querystring = {"path": sdpath.path, "openmode": openmode}
        header = {
            'Authorization': 'Bearer ' + self._auth.get_id_token(),
            Config.get_svc_appkey_name(): Config.get_svc_appkey()
        }
        self.update_header_if_data_partition_id_provided(header)

        resp = requests.put(url=url, headers=header, params=querystring,verify=Config.get_ssl_verify())

        if resp.status_code != 200:
            raise Exception('\n[' + str(resp.status_code) + '] ' + resp.text)

        return resp.json()


    def dataset_unlock(self, sdpath):

        sdpath = SDPath(sdpath)
        url = (Config.get_svc_url()
               + '/dataset/tenant/'
               + sdpath.tenant
               + '/subproject/'
               + sdpath.subproject
               + '/dataset/'
               + sdpath.dataset
               + '/unlock')

        querystring = {"path": sdpath.path}
        header = {
            'Authorization': 'Bearer ' + self._auth.get_id_token(),
            Config.get_svc_appkey_name(): Config.get_svc_appkey()
        }
        self.update_header_if_data_partition_id_provided(header)

        resp = requests.put(url=url, headers=header, params=querystring,verify=Config.get_ssl_verify())

        if resp.status_code != 200:
            raise Exception('\n[' + str(resp.status_code) + '] ' + resp.text)

    def dataset_patch(self, sdpath, patch, closeid=None):

        sdpath = SDPath(sdpath)

        url = (Config.get_svc_url()
               + '/dataset/tenant/'
               + sdpath.tenant
               + '/subproject/'
               + sdpath.subproject
               + '/dataset/'
               + sdpath.dataset)

        if closeid is None:
            querystring = {"path": sdpath.path}
        else:
            querystring = {"path": sdpath.path, "close": closeid}
        header = {
            'Authorization': 'Bearer ' + self._auth.get_id_token(),
            Config.get_svc_appkey_name(): Config.get_svc_appkey()
        }
        self.update_header_if_data_partition_id_provided(header)

        resp = requests.patch(url=url, headers=header,
                              json=patch, params=querystring,verify=Config.get_ssl_verify())

        if resp.status_code != 200:
            raise Exception('\n[' + str(resp.status_code) + '] ' + resp.text)

        return resp.json()

    def dataset_delete(self, sdpath):

        sdpath = SDPath(sdpath)
        url = (Config.get_svc_url()
               + '/dataset/tenant/'
               + sdpath.tenant
               + '/subproject/'
               + sdpath.subproject
               + '/dataset/'
               + sdpath.dataset)
        querystring = {"path": sdpath.path}
        header = {
            'Authorization': 'Bearer ' + self._auth.get_id_token(),
            Config.get_svc_appkey_name(): Config.get_svc_appkey()
        }
        self.update_header_if_data_partition_id_provided(header)

        resp = requests.delete(url=url, headers=header, params=querystring,verify=Config.get_ssl_verify())

        if resp.status_code != 200:
            raise Exception('\n[' + str(resp.status_code) + '] ' + resp.text)

    def user_register(self, useremail):

        url = Config.get_svc_url() + '/user/'
        header = {
            'Authorization': 'Bearer ' + self._auth.get_id_token(),
            Config.get_svc_appkey_name(): Config.get_svc_appkey()
        }
        self.update_header_if_data_partition_id_provided(header)

        body = {'email': useremail}

        resp = requests.post(url=url, headers=header, json=body, verify=Config.get_ssl_verify())

        if resp.status_code != 200 and resp.status_code != 409:
            raise Exception('\n[' + str(resp.status_code) + '] ' + resp.text)

        return resp.status_code

    def user_system_admin_add(self, email):
        url = Config.get_svc_url() + '/user/systemadmin'
        header = {
            'Authorization': 'Bearer ' + self._auth.get_id_token(),
            Config.get_svc_appkey_name(): Config.get_svc_appkey()
        }
        self.update_header_if_data_partition_id_provided(header)

        body = {
            'email': email
        }
        resp = requests.put(url=url, headers=header, json=body, verify=Config.get_ssl_verify())

        if resp.status_code != 200:
            raise Exception('\n[' + str(resp.status_code) + '] ' + resp.text)

    def user_add(self, sdpath, email, role=None):

        url = Config.get_svc_url() + '/user/'
        header = {
            'Authorization': 'Bearer ' + self._auth.get_id_token(),
            Config.get_svc_appkey_name(): Config.get_svc_appkey()
        }
        self.update_header_if_data_partition_id_provided(header)

        body = {
            'email': email,
            'path': sdpath,
        }

        if role:
            body['group'] = role

        resp = requests.put(url=url, headers=header, json=body, verify=Config.get_ssl_verify())

        if resp.status_code != 200:
            raise Exception('\n[' + str(resp.status_code) + '] ' + resp.text)

    def user_remove(self, sdpath, email):

        url = Config.get_svc_url() + '/user/'
        header = {
            'Authorization': 'Bearer ' + self._auth.get_id_token(),
            Config.get_svc_appkey_name(): Config.get_svc_appkey()
        }
        self.update_header_if_data_partition_id_provided(header)

        body = {
            'email': email,
            'path': sdpath,
        }

        resp = requests.delete(url=url, headers=header, json=body, verify=Config.get_ssl_verify())

        if resp.status_code != 200:
            raise Exception('\n[' + str(resp.status_code) + '] ' + resp.text)

    def user_list(self, sdpath):
        url = Config.get_svc_url() + '/user?sdpath=' + sdpath
        header = {
            'Authorization': 'Bearer ' + self._auth.get_id_token(),
            Config.get_svc_appkey_name(): Config.get_svc_appkey()
        }
        self.update_header_if_data_partition_id_provided(header)

        resp = requests.get(url=url, headers=header, verify=Config.get_ssl_verify())

        if resp.status_code != 200:
            raise Exception('\n[' + str(resp.status_code) + '] ' + resp.text)

        return resp.json()

    def user_roles(self, sdpath):
        url = Config.get_svc_url() + '/user/roles?sdpath=' + sdpath
        header = {
            'Authorization': 'Bearer ' + self._auth.get_id_token(),
            Config.get_svc_appkey_name(): Config.get_svc_appkey()
        }
        self.update_header_if_data_partition_id_provided(header)

        resp = requests.get(url=url, headers=header, verify=Config.get_ssl_verify())

        if resp.status_code != 200:
            raise Exception('\n[' + str(resp.status_code) + '] ' + resp.text)

        return resp.json()

    def app_list(self, sdpath):
        url = Config.get_svc_url() + '/app?sdpath=' + sdpath
        header = {
            'Authorization': 'Bearer ' + self._auth.get_id_token(),
            Config.get_svc_appkey_name(): Config.get_svc_appkey()
        }
        self.update_header_if_data_partition_id_provided(header)

        resp = requests.get(url=url, headers=header, verify=Config.get_ssl_verify())

        if resp.status_code != 200:
            raise Exception('\n[' + str(resp.status_code) + '] ' + resp.text)

        return resp.json()

    def apptrusted_list(self, sdpath):
        url = Config.get_svc_url() + '/app/trusted?sdpath=' + sdpath
        header = {
            'Authorization': 'Bearer ' + self._auth.get_id_token(),
            Config.get_svc_appkey_name(): Config.get_svc_appkey()
        }
        self.update_header_if_data_partition_id_provided(header)

        resp = requests.get(url=url, headers=header, verify=Config.get_ssl_verify())

        if resp.status_code != 200:
            raise Exception('\n[' + str(resp.status_code) + '] ' + resp.text)

        return resp.json()

    def app_register(self, service_email, sdpath):
        url = (Config.get_svc_url()
               + '/app?email='
               + service_email
               + '&sdpath='
               + sdpath)

        header = {
            'Authorization': 'Bearer ' + self._auth.get_id_token(),
            Config.get_svc_appkey_name(): Config.get_svc_appkey()
        }
        self.update_header_if_data_partition_id_provided(header)

        resp = requests.post(url=url, headers=header, verify=Config.get_ssl_verify())

        if resp.status_code != 200:
            raise Exception('\n[' + str(resp.status_code) + '] ' + resp.text)

        return resp.status_code

    def apptrusted_register(self, service_email, sdpath):
        url = (Config.get_svc_url()
               + '/app/trusted?email='
               + service_email
               + '&sdpath='
               + sdpath)

        header = {
            'Authorization': 'Bearer ' + self._auth.get_id_token(),
            Config.get_svc_appkey_name(): Config.get_svc_appkey()
        }
        self.update_header_if_data_partition_id_provided(header)

        resp = requests.post(url=url, headers=header, verify=Config.get_ssl_verify())

        if resp.status_code != 200:
            raise Exception('\n[' + str(resp.status_code) + '] ' + resp.text)

        return resp.status_code

    def set_legatag(self, sdpath):

        url = Config.get_svc_url() + '/ltag?sdpath=' + sdpath

        header = {
            'Authorization': 'Bearer ' + self._auth.get_id_token(),
            Config.get_svc_appkey_name(): Config.get_svc_appkey()
        }
        self.update_header_if_data_partition_id_provided(header)

        resp = requests.get(url=url, headers=header, verify=Config.get_ssl_verify())

        if resp.status_code != 200:
            raise Exception('\n[' + str(resp.status_code) + '] ' + resp.text)

        return resp.json()

    def tenant_register(self, tenant_name, gcpid, esd, email):

        url = Config.get_svc_url() + '/tenant/' + tenant_name
        header = {
            'content-type': 'application/json',
            'Authorization': 'Bearer ' + self._auth.get_id_token(),
            Config.get_svc_appkey_name(): Config.get_svc_appkey()
        }
        self.update_header_if_data_partition_id_provided(header)

        payload = {
            'gcpid': gcpid,
            'esd': esd,
            'user': email,
        }

        resp = requests.post(url=url, headers=header, json=payload, verify=Config.get_ssl_verify())

        if resp.status_code != 200:
            raise Exception('[' + str(resp.status_code) + '] ' + resp.text)

    def get_storage_access_token(self, tenant, subproject, readonly, path=None, name=None):
        sub_project_path = 'sd:%2F%2F' + tenant + '%2F' + subproject
        row = 'true' if readonly else 'false'
        if self._storage_access_token is None or self._storage_exp_time < time.time():
            url = Config.get_svc_url() + "/utility/gcs-access-token?sdpath=" + \
                sub_project_path
            if path != None and name != None:
                url = url + str(path).replace("/", "%2F") + str(name)
            url = url + "&readonly=" + row
            header = {
                'content-type': 'application/json',
                'Authorization': 'Bearer ' + self._auth.get_id_token(),
                Config.get_svc_appkey_name(): Config.get_svc_appkey()
            }
            self.update_header_if_data_partition_id_provided(header)

            resp = requests.get(url=url, headers=header,verify=Config.get_ssl_verify())
            if resp.status_code != 200:
                raise Exception('[' + str(resp.status_code) + '] ' + resp.text)
            self._storage_access_token = json.loads(resp.text)['access_token']
            self._storage_exp_time = time.time() + 3000
        return self._storage_access_token

    def operation_bulkDelete(self, sdpath):

        url = (Config.get_svc_url()
               + '/operation/bulk-delete?path=' + quote(sdpath, safe=''))

        header = {
            'Authorization': 'Bearer ' + self._auth.get_id_token(),
            Config.get_svc_appkey_name(): Config.get_svc_appkey()
        }

        resp = requests.put(url=url, headers=header,verify=Config.get_ssl_verify())

        if resp.status_code != 202:
            raise Exception('\n[' + str(resp.status_code) + '] ' + resp.text)

        return resp.json()

    def operation_bulkDeleteStatus(self, operationId, dataPartitionId):

        url = (Config.get_svc_url()
               + '/operation/bulk-delete/' + operationId)

        header = {
            'Authorization': 'Bearer ' + self._auth.get_id_token(),
            Config.get_svc_appkey_name(): Config.get_svc_appkey(),
            'data-partition-id': dataPartitionId
        }

        resp = requests.get(url=url, headers=header, verify=Config.get_ssl_verify())

        if resp.status_code != 200:
            raise Exception('\n[' + str(resp.status_code) + '] ' + resp.text)

        return resp.json()
    
    def operation_changeTier(self, sdpath, tier):

        url = (Config.get_svc_url()
               + '/operation/change-tier?path=' + quote(sdpath, safe='')
               + '&tier=' + tier)

        header = {
            'Authorization': 'Bearer ' + self._auth.get_id_token(),
            Config.get_svc_appkey_name(): Config.get_svc_appkey()
        }

        resp = requests.put(url=url, headers=header,verify=Config.get_ssl_verify())

        if resp.status_code != 202:
            raise Exception('\n[' + str(resp.status_code) + '] ' + resp.text)

        return resp.json()

    def operation_changeTierStatus(self, operationId, dataPartitionId):

        url = (Config.get_svc_url()
               + '/operation/change-tier/' + operationId)

        header = {
            'Authorization': 'Bearer ' + self._auth.get_id_token(),
            Config.get_svc_appkey_name(): Config.get_svc_appkey(),
            'data-partition-id': dataPartitionId
        }

        resp = requests.get(url=url, headers=header, verify=Config.get_ssl_verify())

        if resp.status_code != 200:
            raise Exception('\n[' + str(resp.status_code) + '] ' + resp.text)

        return resp.json()

    def analytics_list_report(self, dataPartitionId, subproject, filter=None, extension=None):

        url = (Config.get_svc_url()
               + '/analytics/job/'
               + subproject)
                
        querystring = {"filter-date": filter, "extension": extension}

        header = {
            'Authorization': 'Bearer ' + self._auth.get_id_token(),
            Config.get_svc_appkey_name(): Config.get_svc_appkey(),
            'data-partition-id': dataPartitionId
        }

        resp = requests.get(url=url, headers=header, params=querystring, verify=Config.get_ssl_verify())

        if resp.status_code != 200:
            raise Exception('\n[' + str(resp.status_code) + '] ' + resp.text)

        return resp.json()

    def analytics_download_report(self, dataPartitionId, subproject, filter=None, extension=None):

        url = (Config.get_svc_url()
               + '/analytics/job/'
               + subproject
               + '/connection-string')

        querystring = {"filter-date": filter, "extension": extension}

        header = {
            'Authorization': 'Bearer ' + self._auth.get_id_token(),
            Config.get_svc_appkey_name(): Config.get_svc_appkey(),
            'data-partition-id': dataPartitionId
        }

        resp = requests.get(url=url, headers=header, params=querystring, verify=Config.get_ssl_verify(), timeout=10)

        if resp.status_code != 200:
            raise Exception('\n[' + str(resp.status_code) + '] ' + resp.text)

        return json.loads(resp.text)['access_token']

    @staticmethod
    def update_header_if_data_partition_id_provided(header):
        if Config.get_data_partition_id() is not None:
            header['data-partition-id'] = Config.get_data_partition_id()
