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

e2e_test_dataset_prefix = 'ds-'
e2e_test_dataset_01 = e2e_test_dataset_prefix + '0'
e2e_test_dataset_02 = e2e_test_dataset_prefix + '1'
e2e_test_dataset_fsize = (1024, '1.0 KB')

def run_command(capsys):
    status = run()
    output = capsys.readouterr()
    return int(status), str(output.out)

def run():
   import sdlib.__main__
   status = sdlib.__main__.main()
   return status

def set_args(args):
    import sys
    sys.argv = []
    sys.argv = args.split(' ')
    sys.argv.insert(0, "sdutil")

def check_string(text, string):
    return text.find(string) != -1

def verify_conditions(**kwargs):
    errors = []
    for test, result in kwargs.items():
        result, output = str(result).split(';')[0], str(result).split(';')[1]
        if int(result):
            errors.append(test.replace('_', ' ') + " test fails. \n The reason: " + output)
    return errors

def subproject_exist(tenant, subproject, stoken):
    import requests
    from sdlib.shared.config import Config
    ENDPOINT_URL = Config.get_svc_url()
    URL = ENDPOINT_URL + '/subproject/tenant/' + tenant + '/subproject/' + subproject
    headers = {'Authorization':"Bearer " + stoken,
                'data-partition-id':tenant,
                'Content-Type':'application/json'
    }
    response = requests.get(url=URL, headers=headers)
    if (response.status_code != 200): return 1
    return 0

def subproject_register(tenant, subproject, legaltag, stoken):
    import requests
    import time
    from sdlib.shared.config import Config
    ENDPOINT_URL = Config.get_svc_url()
    URL = ENDPOINT_URL + '/subproject/tenant/' + tenant + '/subproject/' + subproject
    headers = {'Authorization':"Bearer " + stoken,
                'data-partition-id':tenant,
                'Content-Type':'application/json',
                'ltag': legaltag
    }
    response = requests.post(url=URL, headers=headers)
    if (response.status_code != 200): return 1
    time.sleep(30)
    return 0
