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

import os
import sys
import io
from glob import glob

import pytest

from test.e2e.utils import set_args, run, e2e_test_dataset_prefix, e2e_test_dataset_01, e2e_test_dataset_02, e2e_test_dataset_fsize


def pytest_addoption(parser):
    parser.addoption("--idtoken", action="store", default="", help="credential token")
    parser.addoption("--sdpath", action="store", default="", help="seismic store path")


@pytest.fixture(scope="session", autouse=True)
def pargs(pytestconfig):
    return TestArgs.from_inputs_args(pytestconfig)

@pytest.fixture(scope="session", autouse=True)
def setup(request, pytestconfig, pargs):
    sdpath = pytestconfig.getoption("sdpath")
    upload_seed_files(sdpath, pargs)

    def teardown():
        cleanup(sdpath, pargs)
    request.addfinalizer(teardown)


def upload_seed_files(sdpath, pargs):

    # upload test seistore dataset 01
    file_sdpath = "/".join([sdpath, e2e_test_dataset_01])
    generate_local_file(e2e_test_dataset_01)
    set_args("cp {local_file} {path} --idtoken={stoken}".format(local_file=e2e_test_dataset_01, path=file_sdpath, stoken=pargs.idtoken))
    run()

    # upload test seistore dataset 02
    file_sdpath = "/".join([sdpath, e2e_test_dataset_02])
    generate_local_file(e2e_test_dataset_02)
    set_args("cp {local_file} {path} --idtoken={stoken}".format(local_file=e2e_test_dataset_02, path=file_sdpath, stoken=pargs.idtoken))
    run()

def generate_local_file(name):
    with open(name, 'wb') as fout:
        fout.write(os.urandom(e2e_test_dataset_fsize[0]))

def cleanup(sdpath, pargs):

    # delete test seistore dataset 01
    file_sdpath = "/".join([sdpath, e2e_test_dataset_01])
    set_args("rm {path} --idtoken={stoken}".format(path=file_sdpath, stoken=pargs.idtoken))
    run()

    # delete test seistore dataset 02
    file_sdpath = "/".join([sdpath, e2e_test_dataset_02])
    set_args("rm {path} --idtoken={stoken}".format(path=file_sdpath, stoken=pargs.idtoken))
    run()

    # delete locat test files
    for filename in glob(e2e_test_dataset_prefix + "*"):
        os.remove(filename)

class TestArgs:
    def __init__(self, stoken, sdpath):
        self.idtoken = stoken
        self.sdpath = sdpath

    @classmethod
    def from_inputs_args(cls, pytestconfig):
        return cls(
            pytestconfig.getoption("idtoken"), 
            pytestconfig.getoption("sdpath"))
