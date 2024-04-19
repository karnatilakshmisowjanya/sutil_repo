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


from test.e2e.utils import set_args, run_command, subproject_exist
import time

sdutil_delete_status = None

def sdutil_rm_subproject(capsys, tenant, subproject, sdpath, idtoken):
    set_args("rm {path} --idtoken={stoken}".format(path=sdpath, stoken=idtoken))
    sdutil_status, output = run_command(capsys)
    subproject_status = subproject_exist(tenant, subproject, idtoken)
    return sdutil_status, subproject_status

def sdutil_mk_subproject(capsys, tenant, subproject,  sdpath, admin, legaltag, idtoken):
    set_args("mk {path} {admin} {legaltag} --idtoken={stoken}".format(path=sdpath, admin=admin, legaltag=legaltag, stoken=idtoken))
    sdutil_status, output = run_command(capsys)
    time.sleep(60)
    subproject_created = subproject_exist(tenant, subproject, idtoken)
    return sdutil_status, subproject_created

def test_subproject(capsys, pargs):
    path = pargs.sdpath
    tenant,subproject = path.split("/")[2],path.split("/")[3]
    admin, legaltag, idtoken = pargs.admin, pargs.legaltag01, pargs.idtoken

    status = subproject_exist(tenant, subproject, idtoken)
    if status : 
        sdutil_delete_status, subproject_delete_status = sdutil_rm_subproject(capsys, tenant, subproject, path, idtoken)
    sdutil_create_status, subproject_create_status = sdutil_mk_subproject(capsys, tenant, subproject,  path, admin, legaltag, idtoken)
    if (None == sdutil_delete_status) :
        sdutil_delete_status, subproject_delete_status = sdutil_rm_subproject(capsys, tenant, subproject, path, idtoken)
    assert not sdutil_create_status
    assert not subproject_create_status
    assert not sdutil_delete_status
    assert subproject_delete_status