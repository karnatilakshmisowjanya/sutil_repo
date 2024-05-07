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


import filecmp
import os
import tempfile
import json
from glob import glob

from test.e2e.utils import check_string, run, run_command, set_args, verify_conditions
from test.e2e.apis import subproject_exist, subproject_register, dataset_exist, dataset_delete, dataset_get
from sdlib.shared.sdpath import SDPath

fname_prefix = 'cp_cmd_test'
local_file_name_01 = fname_prefix + '_local_01.txt'
local_file_name_02 = fname_prefix + '_local_02.txt'
dataset_01 = fname_prefix + '_01.txt'
dataset_02 = fname_prefix + '_02.txt'

test_size = (1024 * 1024, '1.0 MB') # for dev test => test_size = (1024, '1.0 KB')

def setup_module(module):
    with open(local_file_name_01, 'wb') as fout:
        fout.write(os.urandom(test_size[0]))
    
def teardown_module(module):
    for filename in glob(fname_prefix + "*"):
        os.remove(filename)

def test_subproject_for_cp(capsys, pargs) :
    # check subproject exists or create it
    path = pargs.sdpath
    tenant,subproject = path.split("/")[2],path.split("/")[3]
    legaltag, idtoken = pargs.legaltag, pargs.idtoken
    acl_admin, acl_viewer = pargs.acl_admin, pargs.acl_viewer
    status = subproject_exist(tenant, subproject, idtoken, acl_admin, acl_viewer)
    if status :
        status = subproject_register(tenant, subproject, legaltag, idtoken, acl_admin, acl_viewer)
    assert not status, "Subroject {subproject} does not exist and fails to be created".format(subproject=subproject)

def test_sdutil_upload(capsys, pargs):
    # upload simple dataset01
    subproject = pargs.sdpath.split("/")[3]
    status = dataset_exist(subproject, dataset_01, pargs.idtoken)
    if not status :
        dataset_delete(subproject, dataset_01, pargs.idtoken)
    set_args("cp {localfile} {path} --idtoken={stoken}".format(localfile=local_file_name_01, path=(pargs.sdpath + '/' + dataset_01), stoken=pargs.idtoken))
    sdutil_cp_status, sdutil_cp_output = run_command(capsys)
    dataset_created_status = dataset_exist(subproject, dataset_01, pargs.idtoken)
    errors = verify_conditions(sdutil_cp_dataset_01 = str(sdutil_cp_status) + ';' + sdutil_cp_output,
                             dataset_get_after_sdutil_cp_dataset_01 = str(dataset_created_status) + ';' + '-----')
    assert not errors, "errors occured:\n{}".format("\n".join(errors))

def test_sdutil_upload_with_seismicmeta(capsys, pargs):
    # check dataset02 exists and remove it
    subproject = pargs.sdpath.split("/")[3]
    status = dataset_exist(subproject, dataset_02, pargs.idtoken)
    if not status :
        dataset_delete(subproject, dataset_02, pargs.idtoken)
    # upload with meta
    with tempfile.NamedTemporaryFile(delete=False) as tmp_fh:
        name = tmp_fh.name
        val = {
            "kind": SDPath(pargs.sdpath).tenant + ":seistore:seismic2d:1.0.0",
            "data": {"msg": "hello world!"}
        }
        tmp_fh.write(json.dumps(val).encode())
        tmp_fh.flush()
    set_args("cp {localfile} {path} --idtoken={stoken} --seismicmeta={meta}".format(
        localfile=local_file_name_01, path=(pargs.sdpath + '/' + dataset_02), stoken=pargs.idtoken, meta=tmp_fh.name))
    sdutil_upload_with_seismicmeta_status, sdutil_upload_with_seismicmeta_output = run_command(capsys)
    dataset_02_created_status = dataset_exist(subproject, dataset_01, pargs.idtoken)
    # check meta was assigned
    dataset_meta_status = 1
    sdutil_check_seismicmeta_status = 1
    reponse = dataset_get(subproject, dataset_02, pargs.idtoken)
    dataset_meta = json.load(reponse)
    if ("hello world!" ==  dataset_meta['seismicmeta']['data']['msg']) : 
        dataset_meta_status = 0
    set_args("stat {path} --idtoken={stoken} --detailed".format(path=(pargs.sdpath + '/' + dataset_02), stoken=pargs.idtoken))
    sdutil_check_seismicmeta_status, sdutil_check_seismicmeta_output = run_command(capsys)
    if ("hello world!" in sdutil_check_seismicmeta_output) :
        sdutil_check_seismicmeta_status = 0
    os.unlink(name)
    errors = verify_conditions(sdutil_cp_dataset_02 = str(sdutil_upload_with_seismicmeta_status) + ';' + sdutil_upload_with_seismicmeta_output,
                             dataset_get_after_sdutil_cp_dataset_02 = str(dataset_02_created_status) + ';' + '-----',
                             dataset_get_seismicmeta_dataset_02 = str(dataset_meta_status) + ';' + 'Seismicmeta was not found in the dataset metadata',
                             sdutil_stat_seismicmeta_output = str(sdutil_check_seismicmeta_status) + ';' + sdutil_check_seismicmeta_output)
    assert not errors, "errors occured:\n{}".format("\n".join(errors))

def test_sdutil_download(capsys, pargs):
    downloaded_files_exist = 1
    set_args("cp {path} {localfile} --idtoken={stoken}".format(path=(pargs.sdpath + '/' + dataset_02), localfile=local_file_name_02, stoken=pargs.idtoken))
    sdutil_cp_download_status, sdutil_cp_download_output = run_command(capsys)
    if ( filecmp.cmp(local_file_name_01, local_file_name_02) ) : downloaded_files_exist = 0
    errors = verify_conditions(sdutil_cp_download = str(sdutil_cp_download_status) + ';' + sdutil_cp_download_output,
                             downloaded_files_found = str(downloaded_files_exist) + ';' + 'Files are not found after sdutil cp download')
    assert not errors, "errors occured:\n{}".format("\n".join(errors))

# TO DO: 
# 1. sdutil ls
# 2. sdutil patch (all available properties?)
# 3. sdutil unlock
# 4. sdutil mv (inside folder, inside subproject, inside tenant)
# 5. update sdutil rm (below)



def test_sdutil_stat(capsys, pargs):
    set_args("stat {path} --idtoken={stoken}".format(path=(pargs.sdpath + '/' + dataset_01), stoken=pargs.idtoken))
    status, output = run_command(capsys)
    print(output)
    assert not status
    assert check_string(output, "Name: {path}".format(path=pargs.sdpath))
    assert check_string(output, "Size: " + test_size[1])

def test_sdutil_rm(capsys, pargs):
    set_args("rm {path} --idtoken={stoken}".format(path=(pargs.sdpath + '/' + dataset_01), stoken=pargs.idtoken))
    status, output = run_command(capsys)
    print(output)
    assert not status
    set_args("rm {path} --idtoken={stoken}".format(path=(pargs.sdpath + '/' + dataset_02), stoken=pargs.idtoken))
    status, output = run_command(capsys)
    print(output)
    assert not status