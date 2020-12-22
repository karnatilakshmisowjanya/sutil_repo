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


import filecmp
import os
import tempfile
import json
from glob import glob

from test.e2e.utils import check_string, run, run_command, set_args
from sdlib.shared.sdpath import SDPath

fname_prefix = 'cp_cmd_test'
local_file_name_01 = fname_prefix + '_local_01.txt'
local_file_name_02 = fname_prefix + '_local_02.txt'
dataset_01 = fname_prefix + '_01.txt'
dataset_02 = fname_prefix + '_02.txt'

test_size = (1024 * 1024 * 1024, '1.0 MB') # for dev test => test_size = (1024, '1.0 KB')

def setup_module(module):
    with open(local_file_name_01, 'wb') as fout:
        fout.write(os.urandom(test_size[0]))

def teardown_module(module):
    for filename in glob(fname_prefix + "*"):
        os.remove(filename)

def test_sdutil_clean(capsys, pargs):
    set_args("rm {path} --idtoken={stoken}".format(path=(pargs.sdpath + '/' + dataset_01), stoken=pargs.idtoken))
    run_command(capsys)
    set_args("rm {path} --idtoken={stoken}".format(path=(pargs.sdpath + '/' + dataset_02), stoken=pargs.idtoken))
    run_command(capsys)

def test_sdutil_upload(capsys, pargs):
    set_args("cp {localfile} {path} --idtoken={stoken}".format(localfile=local_file_name_01, path=(pargs.sdpath + '/' + dataset_01), stoken=pargs.idtoken))
    status, output = run_command(capsys)
    print(output)
    assert not status


def test_sdutil_upload_with_seismicmeta(capsys, pargs):

    # clean
    set_args("rm {path} --idtoken={stoken}".format(path=(pargs.sdpath + '/' + dataset_02), stoken=pargs.idtoken))
    run()

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
    status = run()
    assert not status
    os.unlink(name)

    # check meta was assigned
    set_args("stat {path} --idtoken={stoken} --detailed".format(path=(pargs.sdpath + '/' + dataset_02), stoken=pargs.idtoken))
    status, output = run_command(capsys)
    print("OUTPUT: %s" % output)
    assert "hello world!" in output


def test_sdutil_download(capsys, pargs):
    set_args("cp {path} {localfile} --idtoken={stoken}".format(path=(pargs.sdpath + '/' + dataset_02), localfile=local_file_name_02, stoken=pargs.idtoken))
    status, output = run_command(capsys)
    print(output)
    assert not status
    assert filecmp.cmp(local_file_name_01, local_file_name_02)


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