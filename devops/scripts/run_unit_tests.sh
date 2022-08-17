#!/bin/bash
# ============================================================================
# Copyright 2017-2020, Schlumberger
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
# ============================================================================

# parse input parameters
for i in "$@"; do
    case $i in
        --mnt-volume=*)
            mnt_volume="${i#*=}"
            shift
            ;;  
        *)
            echo "unknown option: $i"
            exit 1
            ;;
    esac
done

# set the mount volume if not set as input argument
if [ -z "${mnt_volume}" ]; then
    mnt_volume="$(pwd)"
fi
cd ${mnt_volume}

# create temporary configuration for unit test
cp sdlib/config.sample.yaml config_original.yaml
mv sdlib/config.sample.yaml sdlib/config.yaml
echo "seistore:" > sdlib/config.yaml
echo "    service: '{\"provider\": {\"env\" : {\"url\": \"dummy-url\", \"appkey\": \"dummy-apkey\"}}}'" >> sdlib/config.yaml
echo "auth_provider:" >> sdlib/config.yaml
echo "    default: \"oauth2\"" >> sdlib/config.yaml

# remove previous coverage generations
rm -rf .coverage coverage coverage.xml TEST-*

# run unit test only
# pytest test/utest
# run unit test and generate coverage
coverage run --branch --omit="*/*__init__.py" --source=sdlib -m xmlrunner discover -v -s test/utest/ -p "test_*.py"
exit_status=$?

# generate coverage report
coverage html -d coverage
coverage xml -o coverage/coverage.xml

# chnage directory permission
chmod -R 777 coverage

# restore configuration and clear temporary files
cp config_original.yaml sdlib/config.sample.yaml
rm config_original.yaml
rm sdlib/config.yaml
if [ $exit_status -ne 0 ]; then exit 1; fi
