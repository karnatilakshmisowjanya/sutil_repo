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


import os
import tempfile
import json
import time

from test.e2e.utils import run_command, set_args, verify_conditions, e2e_test_dataset_01, e2e_test_dataset_02
from test.e2e.apis import *


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

def test_sdutil_cp_upload(capsys, pargs):
    # check dataset01 exists and remove it
    path = pargs.sdpath
    tenant,subproject = path.split("/")[2],path.split("/")[3]
    status, dataset_exist_output = dataset_exist(tenant, subproject, e2e_test_dataset_01, pargs.idtoken)
    if 0 == status :
        delete_status, delete_output = dataset_delete(tenant, subproject, e2e_test_dataset_01, pargs.idtoken)
        if 0 != delete_status : assert not delete_status, delete_output
    # upload simple dataset01
    set_args("cp {localfile} {path} --idtoken={stoken}".format(localfile=e2e_test_dataset_01, path=(pargs.sdpath + '/' + e2e_test_dataset_01), stoken=pargs.idtoken))
    sdutil_cp_status, sdutil_cp_output = run_command(capsys)
    dataset_created_status, dataset_exist_output = dataset_exist(tenant, subproject, e2e_test_dataset_01, pargs.idtoken)
    errors = verify_conditions(sdutil_cp_dataset_01 = str(sdutil_cp_status) + ';' + sdutil_cp_output,
                             dataset_get_after_sdutil_cp_dataset_01 = str(dataset_created_status) + ';' +  str(dataset_exist_output) )
    assert not errors, "errors occured:\n{}".format("\n".join(errors))

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
        localfile=e2e_test_dataset_02, path=(pargs.sdpath + '/' + e2e_test_dataset_02), stoken=pargs.idtoken, meta=name))
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

def test_sdutil_stat_dataset(capsys, pargs):
    set_args("stat {path} --idtoken={stoken} --detailed".format(path=(pargs.sdpath + '/' + e2e_test_dataset_02), stoken=pargs.idtoken))
    sdutil_stat_status, sdutil_check_seismicmeta_output = run_command(capsys)
    sdutil_check_seismicmeta_status = 1
    if ("hello world!" in sdutil_check_seismicmeta_output) :
        sdutil_check_seismicmeta_status = 0
    errors = verify_conditions(sdutil_stat_dataset_02 = str(sdutil_stat_status) + ';' + sdutil_check_seismicmeta_output,
                               sdutil_stat_seismicmeta_output = str(sdutil_check_seismicmeta_status) + ';' + sdutil_check_seismicmeta_output)
    assert not errors, "errors occured:\n{}".format("\n".join(errors))

def test_sdutil_ls_dataset(capsys, pargs):
    # verify sdutil ls without options
    path = pargs.sdpath
    tenant,subproject = path.split("/")[2],path.split("/")[3]
    ## get list of datasets through SDMS endpoints in root path
    response = utility_ls(path, stoken=pargs.idtoken)
    if (response.status_code != 200) : assert False, '[' + str(response.status_code) + ']: ' + str(response.content)
    utility_api_list = json.loads(response.content)
    ## get list of datasets through SDUTIL command in root path
    set_args("ls {path} --idtoken={stoken}".format(path=path, stoken=pargs.idtoken))
    sdutil_ls_status, sdutil_ls_output = run_command(capsys)
    dataset_sdutil_list = sdutil_ls_output.split('\n')[1:-2] # remove empty lines
    ## compare lists
    list_match = 1 if (sorted(dataset_sdutil_list) != sorted(utility_api_list)) else 0
    
    # verify -rl options work
    ## get list of datasets through SDUTIL command in the whole subproject
    set_args("ls {path} -rl --idtoken={stoken}".format(path=path, stoken=pargs.idtoken))
    sdutil_full_list_status, sdutil_full_list_output = run_command(capsys)
    sdutil_full_list = sdutil_full_list_output.split('\n')[1:-2]
    sdutil_dataset_full_list = []
    for item in sdutil_full_list: sdutil_dataset_full_list.append(item.split('/')[-1])
    ## get list of datasets through SDMS endpoints in the whole subproject
    dataset_list_response = dataset_list(tenant, subproject, stoken=pargs.idtoken)
    api_full_list = json.loads(dataset_list_response.content)
    dataset_api_full_list = [d['name'] for d in api_full_list]
    full_list_match = 1 if (sorted(sdutil_dataset_full_list) != sorted(dataset_api_full_list)) else 0
    
    # checks
    errors = verify_conditions(sdutil_ls_dataset = str(sdutil_ls_status) + ';' + sdutil_ls_output,
                               compare_list = str(list_match) + ';' + 'Dataset lists are not the same for SDUTIL and SDMS API requests.\n' + 'SDUTIL list:\n' + "{}".format('\n'.join(dataset_sdutil_list)) + '\nSDMS API list:\n' + "{}".format('\n'.join(utility_api_list)),
                               sdutil_ls_dataset_with_options = str(sdutil_full_list_status) + ';' + sdutil_full_list_output,
                               compare_full_list = str(full_list_match) + ';' + 'Dataset list with options are not the same for SDUTIL and SDMS API requests.\n' + 'SDUTIL list:\n' + "{}".format('\n'.join(sdutil_dataset_full_list)) + '\nSDMS API list:\n' + "{}".format('\n'.join(dataset_api_full_list))
                            )
    assert not errors, "errors occured:\n{}".format("\n".join(errors))

def test_sdutil_patch(capsys, pargs):
    path = pargs.sdpath + '/' + e2e_test_dataset_01
    tenant,subproject = path.split("/")[2],path.split("/")[3]
    dataset_exist_status, dataset_exist_output = dataset_exist(tenant, subproject, e2e_test_dataset_01, pargs.idtoken)
    if 0 != dataset_exist_status : assert not dataset_exist_status, dataset_exist_output
    # change legaltag
    set_args("patch {path} --idtoken={stoken} --ltag={legaltag}".format(path=path, stoken=pargs.idtoken, legaltag=pargs.legaltag02))
    sdutil_patch_legaltag_status, sdutil_patch_legaltag_output = run_command(capsys)
    # change readonly status
    set_args("patch {path} --idtoken={stoken} --readonly={readonly}".format(path=path, stoken=pargs.idtoken, readonly=True))
    sdutil_patch_readonly_status, sdutil_patch_readonly_output = run_command(capsys)
    # verify the changes
    dataset_get_response = dataset_get(tenant, subproject, e2e_test_dataset_01, pargs.idtoken)
    content = json.loads(dataset_get_response.content)
    verify_legaltag_patch = 1 if content['ltag'] != pargs.legaltag02 else 0
    verify_readonly_patch = 1 if content['readonly'] != True else 0
    # revert changes
    set_args("patch {path} --idtoken={stoken} --ltag={legaltag} --readonly={readonly}".format(path=path, stoken=pargs.idtoken, legaltag=pargs.legaltag, readonly=False))
    sdutil_patch_revert_status, sdutil_patch_revert_output = run_command(capsys)
     # verify rollback
    dataset_get_revert_response = dataset_get(tenant, subproject, e2e_test_dataset_01, pargs.idtoken)
    revert_content = json.loads(dataset_get_revert_response.content)
    verify_rollback_legaltag = 1 if revert_content['ltag'] != pargs.legaltag else 0
    verify_rollback_readonly = 1 if revert_content['readonly'] != False else 0
    errors = verify_conditions(sdutil_patch_dataset_legaltag = str(sdutil_patch_legaltag_status) + ';' + sdutil_patch_legaltag_output,
                                verify_legaltag_change = str(verify_legaltag_patch) + ';' + 'The dataset legaltag was not patched',
                                sdutil_patch_dataset_readonly = str(sdutil_patch_readonly_status) + ';' + sdutil_patch_readonly_output,
                                verify_readonly_patch = str(verify_readonly_patch) + ';' + 'The dataset was not patched for readonly mode',
                                sdutil_patch_dataset_metadata_revertion = str(sdutil_patch_revert_status) + ';' + sdutil_patch_revert_output,
                                verify_legaltag_revertion = str(verify_rollback_legaltag) + ';' + 'The dataset legaltag was not reverted',
                                verify_readonly_revertion = str(verify_rollback_readonly) + ';' + 'The dataset readonly mode was not reverted'
                                )
    assert not errors, "errors occured:\n{}".format("\n".join(errors))

# def test_sdutil_mv(capsys, pargs):
#     path = pargs.sdpath + '/' + e2e_test_dataset_01
#     destination_path = '/test-folder/'
#     tenant,subproject = path.split("/")[2],path.split("/")[3]
#     status, dataset_exist_output = dataset_exist(tenant, subproject, e2e_test_dataset_01, pargs.idtoken)
#     if 0 != status : assert not status, dataset_exist_output
#     status, dataset_exist_output = dataset_exist(tenant, subproject, e2e_test_dataset_01, pargs.idtoken, destination_path)
#     if 0 == status : 
#         remove_status, remove_output = dataset_delete(tenant, subproject, e2e_test_dataset_01, pargs.idtoken, destination_path)
#         if 0 != remove_status: assert not remove_status, remove_output
#     # move the dataset into a folder and verify it is moved
#     set_args("mv {sdpath_from} {sdpath_to} --idtoken={stoken}".format(sdpath_from=path, sdpath_to=pargs.sdpath + destination_path + e2e_test_dataset_01, stoken=pargs.idtoken))
#     sdutil_mv_status, sdutil_mv_output = run_command(capsys)
#     dataset_get_negative_response = dataset_get(tenant, subproject, e2e_test_dataset_01, pargs.idtoken)
#     negative_response = json.loads(dataset_get_negative_response.content)
#     verify_dataset_removed = 1 if negative_response.status_code != 404 else 0
#     dataset_get_positive_response = dataset_get(tenant, subproject, e2e_test_dataset_01, pargs.idtoken, destination_path)
#     positive_response = json.loads(dataset_get_positive_response.content)
#     verify_dataset_moved_into_folder = 1 if positive_response.status_code != 404 else 0
#     errors = verify_conditions(sdutil_mv_dataset_into_folder = str(sdutil_mv_status) + ';' + sdutil_mv_output,
#                                 verify_dataset_removed_from_old_place = str(verify_dataset_removed) + ';' + 'The dataset was not removed from old sdpath',
#                                 verify_dataset_moved_into_new_destination = str(verify_dataset_moved_into_folder) + ';' + 'The dataset was not moved to a new sdpath'
#                                 )
#     assert not errors, "errors occured:\n{}".format("\n".join(errors))

def test_sdutil_rm_dataset(capsys, pargs):
    path = pargs.sdpath + '/' + e2e_test_dataset_02
    tenant,subproject = path.split("/")[2],path.split("/")[3]
    # verify the dataset exist
    status, dataset_exist_output = dataset_exist(tenant, subproject, e2e_test_dataset_02, pargs.idtoken)
    if 0 != status : assert not status, dataset_exist_output
    # remove the dataset and verify it is removed
    set_args("rm {path} --idtoken={stoken}".format(path=path, stoken=pargs.idtoken))
    sdutil_status, sdutil_rm_output = run_command(capsys)
    set_args("rm {path} --idtoken={stoken}".format(path=pargs.sdpath + '/test-folder/' + e2e_test_dataset_01, stoken=pargs.idtoken))
    sdutil_status, sdutil_rm_output = run_command(capsys)
    time.sleep(5)
    dataset_exist_status, dataset_exist_output = dataset_exist(tenant, subproject, e2e_test_dataset_02, pargs.idtoken)
    verify_deletion = 1 if (dataset_exist_status == 0) else 0
    errors = verify_conditions(sdutil_rm_dataset = str(sdutil_status) + ';' + sdutil_rm_output,
                                verify_dataset_deleted = str(verify_deletion) + ';' + 'Dataset still exist after sdutil rm operation')
    assert not errors, "errors occured:\n{}".format("\n".join(errors))
    


# # TO DO: 
# # (DONE) 1. sdutil ls
# # (DONE) 2. sdutil patch (all available properties?)
# # 3. sdutil unlock
# # 4. sdutil mv (inside subproject, inside tenant?)
# # (DONE) 5. update sdutil rm

# def test_sdutil_unlock(capsys, pargs):
#     path = pargs.sdpath + '/' + e2e_test_dataset_01
#     tenant,subproject = path.split("/")[2],path.split("/")[3]
#     # verify the dataset exist and put write lock on it
#     status, dataset_exist_output = dataset_exist(tenant, subproject, e2e_test_dataset_01, pargs.idtoken)
#     if 0 != status : assert not status, dataset_exist_output
#     # dataset_lock_status, dataset_lock_output = dataset_lock(tenant, subproject, e2e_test_dataset_01, pargs.idtoken)
#     dataset_lock_response = dataset_lock(tenant, subproject, e2e_test_dataset_01, pargs.idtoken, 'write')
#     if 200 != dataset_lock_response.status_code : assert False, dataset_lock_response.content
#     # if 0 != dataset_lock_status : assert not dataset_lock_status, dataset_lock_output
#     # response = dataset_get(tenant, subproject, e2e_test_dataset_01, pargs.idtoken)
#     dataset_lock2_response = dataset_lock(tenant, subproject, e2e_test_dataset_01, pargs.idtoken, 'read')
#     if 423 != dataset_lock2_response.status_code : assert False, 'The dataset was not locked'
#     # test sdutil unlock
#     set_args("unlock {path} --idtoken={stoken}".format(path=path, stoken=pargs.idtoken))
#     sdutil_unlock_status, sdutil_unlock_output = run_command(capsys)
#     # dataset_get_response = dataset_get(tenant, subproject, e2e_test_dataset_01, pargs.idtoken)
#     dataset_get_after_unlock_status = 1 if 200 != dataset_get_response.status_code else 0
#     errors = verify_conditions(sdutil_unlock_dataset = str(sdutil_unlock_status) + ';' + sdutil_unlock_output,
#                                 dataset_get_after_unlock = str(dataset_get_after_unlock_status) + ';' + dataset_get_response.content)
#     assert not errors, "errors occured:\n{}".format("\n".join(errors))