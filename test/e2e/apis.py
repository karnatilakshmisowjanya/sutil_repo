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

import requests
from sdlib.shared.config import Config
import time

def subproject_exist(tenant, subproject, stoken):
    ENDPOINT_URL = Config.get_svc_url()
    URL = ENDPOINT_URL + '/subproject/tenant/' + tenant + '/subproject/' + subproject
    headers = {'Authorization':"Bearer " + stoken,
                'data-partition-id':tenant,
                'Content-Type':'application/json'
    }
    response = requests.get(url=URL, headers=headers)
    if (response.status_code != 200): return 1
    return 0

def subproject_register(tenant, subproject, legaltag, stoken, *args):
    ENDPOINT_URL = Config.get_svc_url()
    URL = ENDPOINT_URL + '/subproject/tenant/' + tenant + '/subproject/' + subproject
    headers = {'Authorization':"Bearer " + stoken,
                'data-partition-id':tenant,
                'Content-Type':'application/json',
                'ltag': legaltag
    }
    body = {}
    if args :
        body = {"acls": {"admins": args.acl_admin,
                           "viewers": args.acl_viewer}
        }
    response = requests.post(url=URL, headers=headers, body=body)
    if (response.status_code != 200): return 1
    time.sleep(30)
    return 0

def subproject_delete(tenant, subproject, stoken):
    ENDPOINT_URL = Config.get_svc_url()
    URL = ENDPOINT_URL + '/subproject/tenant/' + tenant + '/subproject/' + subproject
    headers = {'Authorization':"Bearer " + stoken,
                'data-partition-id':tenant,
                'Content-Type':'application/json'
    }
    response = requests.delete(url=URL, headers=headers)
    if (response.status_code != 200): return 1
    return 0

def dataset_exist(subproject, dataset, stoken):
    from urllib.parse import quote_plus
    ENDPOINT_URL = Config.get_svc_url()
    TENANT = Config.get_data_partition_id()
    URL = ENDPOINT_URL + '/seistore-svc/api/v3/dataset/tenant/' + TENANT + '/subproject/' + subproject + '/dataset/' + dataset
    headers = {'Authorization':"Bearer " + stoken,
                'data-partition-id':TENANT,
                'Content-Type':'application/json'
    }
    path = quote_plus(path)
    params = {'path':path}
    response = requests.get(url=URL, headers=headers, params=params)
    if (response.status_code != 200): return 1
    return 0

def dataset_delete(subproject, dataset, stoken):
    ENDPOINT_URL = Config.get_svc_url()
    TENANT = Config.get_data_partition_id()
    URL = ENDPOINT_URL + '/seistore-svc/api/v3/dataset/tenant/' + TENANT + '/subproject/' + subproject + '/dataset/' + dataset
    headers = {'Authorization':"Bearer " + stoken,
                'data-partition-id':TENANT,
                'Content-Type':'application/json'
    }
    response = requests.delete(url=URL, headers=headers)
    if (response.status_code != 200): return 1
    return 0

def dataset_get(subproject, dataset, stoken):
    from urllib.parse import quote_plus
    ENDPOINT_URL = Config.get_svc_url()
    TENANT = Config.get_data_partition_id()
    URL = ENDPOINT_URL + '/seistore-svc/api/v3/dataset/tenant/' + TENANT + '/subproject/' + subproject + '/dataset/' + dataset
    headers = {'Authorization':"Bearer " + stoken,
                'data-partition-id':TENANT,
                'Content-Type':'application/json'
    }
    path = quote_plus(path)
    params = {'path':path}
    response = requests.get(url=URL, headers=headers, params=params)
    return response