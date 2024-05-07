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


from test.e2e.utils import set_args, run_command, verify_conditions
from test.e2e.apis import subproject_exist, subproject_delete
import time

def sdutil_rm_subproject(capsys, tenant, subproject, sdpath, idtoken):
    set_args("rm {path} --idtoken={stoken}".format(path=sdpath, stoken=idtoken))
    sdutil_status, output = run_command(capsys)
    subproject_status = subproject_exist(tenant, subproject, idtoken)
    if subproject_status : subproject_status = 0 # operation succeed because we expect 404 response after deletion
    return sdutil_status, subproject_status, output

def sdutil_mk_subproject(capsys, tenant, subproject, sdpath, admin, legaltag, idtoken, acl_admin, acl_viewer):
    set_args("mk {path} {admin} {legaltag} --admin_acl={acl_admin} --viewer_acl={acl_viewer} --idtoken={stoken}".format(path=sdpath, admin=admin, legaltag=legaltag, stoken=idtoken, acl_admin=acl_admin, acl_viewer=acl_viewer))
    sdutil_status, output = run_command(capsys)
    time.sleep(60)
    subproject_created = subproject_exist(tenant, subproject, idtoken)
    return sdutil_status, subproject_created, output

def sdutil_stat_subproject(capsys, sdpath, idtoken):
    set_args("stat {path} --idtoken={stoken}".format(path=sdpath, stoken=idtoken))
    status, output = run_command(capsys)
    return status, output

def test_subproject(capsys, pargs):
    path = pargs.sdpath
    tenant,subproject = path.split("/")[2],path.split("/")[3]
    admin, legaltag, idtoken = pargs.admin, pargs.legaltag, pargs.idtoken
    acl_admin, acl_viewer = pargs.acl_admin, pargs.acl_viewer
    status = subproject_exist(tenant, subproject, idtoken)
    if 0 != status :
        subproject_delete(tenant, subproject, idtoken)
    # sdutil mk sd://tenant/subproject (Test subproject creation)
    sdutil_create_status, subproject_create_status, sdutil_mk_output = sdutil_mk_subproject(capsys, tenant, subproject, path, admin, legaltag, idtoken, acl_admin, acl_viewer)
    # sdutil stat sd://tenant/subproject (Test get subproject metadata)
    sdutil_stat_status, sdutil_stat_output = sdutil_stat_subproject(capsys, path, idtoken)
    # sdutil rm sd://tenant/subproject
    sdutil_delete_status, subproject_delete_status, sdutil_rm_output = sdutil_rm_subproject(capsys, tenant, subproject, path, idtoken)
    # assert the results
    errors = verify_conditions(sdutil_mk_subproject = str(sdutil_create_status) + ';' + sdutil_mk_output,
                             subroject_get_after_sdutil_mk_subproject = str(subproject_create_status) + ';' + '-----',
                             sdutil_stat_subproject = str(sdutil_stat_status) + ';' + sdutil_stat_output,
                             sdutil_rm_subproject = str(sdutil_delete_status) + ';' + sdutil_rm_output,
                             subroject_get_after_sdutil_rm_subproject = str(subproject_delete_status) + ';' + '-----')
    assert not errors, "errors occured:\n{}".format("\n".join(errors))

    # TO DO: sdutil ls subprojects