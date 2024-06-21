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
import time
from glob import glob

from test.e2e.utils import check_string, run, run_command, set_args, verify_conditions, e2e_test_dataset_prefix, e2e_test_dataset_01, e2e_test_dataset_02
from test.e2e.apis import subproject_exist, subproject_register, dataset_exist, dataset_delete, dataset_get
from sdlib.shared.sdpath import SDPath


def test_subproject_for_cp(capsys, pargs) :
    # check subproject exists or create it
    path = pargs.sdpath
    tenant,subproject = path.split("/")[2],path.split("/")[3]
    legaltag, idtoken = pargs.legaltag, pargs.idtoken
    acl_admin, acl_viewer = pargs.acl_admin, pargs.acl_viewer
    status = subproject_exist(tenant, subproject, idtoken)
    if 0 != status :
        status, output = subproject_register(tenant, subproject, legaltag, idtoken, admins=acl_admin, viewers=acl_viewer)
    assert not status, output

# def test_sdutil_cp_upload(capsys, pargs):
#     # check dataset01 exists and remove it
#     path = pargs.sdpath
#     tenant,subproject = path.split("/")[2],path.split("/")[3]
#     status, dataset_exist_output = dataset_exist(tenant, subproject, e2e_test_dataset_01, pargs.idtoken)
#     if 0 == status :
#         delete_status, delete_output = dataset_delete(tenant, subproject, e2e_test_dataset_01, pargs.idtoken)
#         if 0 != delete_status : assert not delete_status, delete_output
    
#     # upload simple dataset01
#     set_args("cp {localfile} {path} --idtoken={stoken}".format(localfile=e2e_test_dataset_01, path=(pargs.sdpath + '/' + e2e_test_dataset_01), stoken=pargs.idtoken))
#     sdutil_cp_status, sdutil_cp_output = run_command(capsys)
#     dataset_created_status, dataset_exist_output = dataset_exist(tenant, subproject, e2e_test_dataset_01, pargs.idtoken)
    
#     errors = verify_conditions(sdutil_cp_dataset_01 = str(sdutil_cp_status) + ';' + sdutil_cp_output,
#                              dataset_get_after_sdutil_cp_dataset_01 = str(dataset_created_status) + ';' +  str(dataset_exist_output) )
#     assert not errors, "errors occured:\n{}".format("\n".join(errors))

def test_sdutil_cp_upload_with_seismicmeta(capsys, pargs): # Has conflict with dataset_01 creation
    # check dataset02 exists and remove it
    path = pargs.sdpath
    tenant,subproject = path.split("/")[2],path.split("/")[3]
    status, dataset_exist_output = dataset_exist(tenant, subproject, e2e_test_dataset_02, pargs.idtoken)
    if 0 == status :
        delete_status, delete_output = dataset_delete(tenant, subproject, e2e_test_dataset_02, pargs.idtoken)
        if 0 != delete_status : assert not delete_status, delete_output
        time.sleep(5)

    # upload with meta
    with tempfile.NamedTemporaryFile(delete=False) as tmp_fh:
        name = tmp_fh.name
        val = {
            "kind": tenant + ":seistore:seismic2d:1.0.0",
            "data": {"msg": "hello world!"}
        }
        tmp_fh.write(json.dumps(val).encode())
        tmp_fh.flush()

    set_args("cp {localfile} {path} --idtoken={stoken} --seismicmeta={meta}".format(
        localfile=e2e_test_dataset_02, path=(pargs.sdpath + '/' + e2e_test_dataset_02), stoken=pargs.idtoken, meta=tmp_fh.name))
    sdutil_upload_with_seismicmeta_status, sdutil_upload_with_seismicmeta_output = run_command(capsys)
    if 0 != sdutil_upload_with_seismicmeta_status : assert not sdutil_upload_with_seismicmeta_status, sdutil_upload_with_seismicmeta_output
    time.sleep(5)
    dataset_02_created_status, dataset_exist_output = dataset_exist(tenant, subproject, e2e_test_dataset_02, pargs.idtoken)
    if 0 != dataset_02_created_status : assert not dataset_02_created_status, dataset_exist_output
    
    # check meta was assigned
    dataset_meta_status = 1
    reponse = dataset_get(tenant, subproject, e2e_test_dataset_02, pargs.idtoken)
    dataset_meta = json.loads(reponse.content)
    if ("hello world!" ==  dataset_meta['seismicmeta']['data']['msg']) : 
        dataset_meta_status = 0
    os.unlink(name)

    errors = verify_conditions(sdutil_cp_dataset_02 = str(sdutil_upload_with_seismicmeta_status) + ';' + sdutil_upload_with_seismicmeta_output,
                             dataset_get_after_sdutil_cp_dataset_02 = str(dataset_02_created_status) + ';' + str(dataset_exist_output),
                             dataset_get_seismicmeta_dataset_02 = str(dataset_meta_status) + ';' + 'Seismicmeta was not found in the dataset metadata')
    assert not errors, "errors occured:\n{}".format("\n".join(errors))

def test_sdutil_stat_dataset(capsys, pargs):
    set_args("stat {path} --idtoken={stoken} --detailed".format(path=(pargs.sdpath + '/' + e2e_test_dataset_02), stoken=pargs.idtoken))
    sdutil_stat_status, sdutil_check_seismicmeta_output = run_command(capsys)
    sdutil_check_seismicmeta_status = 1
    if ("hello world!" in sdutil_check_seismicmeta_output) :
        sdutil_check_seismicmeta_status = 0
    
    errors = verify_conditions(sdutil_stat_dataset_02 = str(sdutil_stat_status) + ';' + sdutil_check_seismicmeta_output,
                               sdutil_stat_seismicmeta_output = str(sdutil_check_seismicmeta_status) + ';' + sdutil_check_seismicmeta_output)
    assert not errors, "errors occured:\n{}".format("\n".join(errors))

def test_sdutil_cp_download(capsys, pargs):
    from pathlib import Path
    downloaded_files_exist = 1
    local_file_name_01 = os.getcwd() + '\\local-' + e2e_test_dataset_01
    original_file = os.getcwd() + '\\' + e2e_test_dataset_01
    set_args("cp {path} {localfile} --idtoken={stoken} --force".format(path=(pargs.sdpath + '/' + e2e_test_dataset_01), localfile=local_file_name_01, stoken=pargs.idtoken))
    sdutil_cp_download_status, sdutil_cp_download_output = run_command(capsys)
    # if ( filecmp.cmp(local_file_name_01, original_file) ) : downloaded_files_exist = 0
    if os.path.isfile(local_file_name_01) : downloaded_files_exist = 0
    errors = verify_conditions(sdutil_cp_download = str(sdutil_cp_download_status) + ';' + sdutil_cp_download_output,
                             downloaded_files_found = str(downloaded_files_exist) + ';' + 'Files are not found after sdutil cp download')
    assert not errors, "errors occured:\n{}".format("\n".join(errors))



# # TO DO: 
# # 1. sdutil ls
# # 2. sdutil patch (all available properties?)
# # 3. sdutil unlock
# # 4. sdutil mv (inside folder, inside subproject, inside tenant)
# # 5. update sdutil rm (below)



# def test_sdutil_stat(capsys, pargs):
#     set_args("stat {path} --idtoken={stoken}".format(path=(pargs.sdpath + '/' + dataset_01), stoken=pargs.idtoken))
#     status, output = run_command(capsys)
#     print(output)
#     assert not status
#     assert check_string(output, "Name: {path}".format(path=pargs.sdpath))
#     assert check_string(output, "Size: " + test_size[1])

# def test_sdutil_rm(capsys, pargs):
#     set_args("rm {path} --idtoken={stoken}".format(path=(pargs.sdpath + '/' + dataset_01), stoken=pargs.idtoken))
#     status, output = run_command(capsys)
#     print(output)
#     assert not status
#     set_args("rm {path} --idtoken={stoken}".format(path=(pargs.sdpath + '/' + dataset_02), stoken=pargs.idtoken))
#     status, output = run_command(capsys)
#     print(output)
#     assert not status