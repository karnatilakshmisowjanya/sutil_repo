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


import time
from test.e2e.utils import set_args, run_command, verify_conditions
from test.e2e.apis import subproject_exist, subproject_delete


def test_subproject(capsys, pargs):
    path, idtoken = pargs.sdpath, pargs.idtoken
    tenant,subproject = path.split("/")[2],path.split("/")[3]
    status, output = subproject_delete(tenant, subproject, idtoken)
    time.sleep(10)
    assert not status, output

def test_sdutil_mk_subproject(capsys, pargs):
    path = pargs.sdpath
    tenant,subproject = path.split("/")[2],path.split("/")[3]
    admin, legaltag, idtoken = pargs.admin, pargs.legaltag, pargs.idtoken
    acl_admin, acl_viewer = pargs.acl_admin, pargs.acl_viewer
    set_args("mk {path} {admin} {legaltag} --admin_acl={acl_admin} --viewer_acl={acl_viewer} --idtoken={stoken}".format(path=path, admin=admin, legaltag=legaltag, stoken=idtoken, acl_admin=acl_admin, acl_viewer=acl_viewer))
    sdutil_mk_status, sdutil_mk_output = run_command(capsys)
    time.sleep(60)
    subproject_created = subproject_exist(tenant, subproject, idtoken)
    errors = verify_conditions( sdutil_mk_subproject = str(sdutil_mk_status) + ';' + sdutil_mk_output,
                                verify_subproject_exist_after_creation = str(subproject_created) + ';' + 'Subproject does not found after sdutil mk command'
                            )
    assert not errors, "errors occured:\n{}".format("\n".join(errors))

def test_sdutil_stat_subproject(capsys, pargs):
    set_args("stat {path} --idtoken={stoken}".format(path=pargs.sdpath, stoken=pargs.idtoken))
    sdutil_stat_status, sdutil_stat_output = run_command(capsys)
    assert not sdutil_stat_status, sdutil_stat_output

def test_sdutil_ls_subprojects(capsys, pargs):
    set_args("ls {path} --idtoken={stoken}".format(path=pargs.sdpath, stoken=pargs.idtoken))
    sdutil_list_status, sdutil_list_output = run_command(capsys)
    assert not sdutil_list_status, sdutil_list_output

def test_sdutil_rm_subproject(capsys, pargs):
    path = pargs.sdpath
    tenant,subproject = path.split("/")[2],path.split("/")[3]
    set_args("rm {path} --idtoken={stoken}".format(path=path, stoken=pargs.idtoken))
    sdutil_rm_status, sdutil_rm_output = run_command(capsys)
    time.sleep(10)
    subproject_status = subproject_exist(tenant, subproject, pargs.idtoken)
    subproject_delete_status = 0 if 1 == subproject_status else 1 # operation succeed because we expect 404 response after deletion
    errors = verify_conditions( sdutil_rm_subproject = str(sdutil_rm_status) + ';' + sdutil_rm_output,
                                subroject_get_after_sdutil_rm_subproject = str(subproject_delete_status) + ';' + 'Subproject exists after sdutil rm command')
    assert not errors, "errors occured:\n{}".format("\n".join(errors))