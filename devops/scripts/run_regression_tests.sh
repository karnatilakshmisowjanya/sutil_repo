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
        --cloud-provider=*) # required
            provider="${i#*=}"
            shift
            ;;
        --service-url=*) # required
            service_url="${i#*=}"
            shift
            ;;
        --service-key=*) # required
            service_key="${i#*=}"
            shift
            ;;
        --idtoken=*) # required
            idtoken="${i#*=}"
            shift
            ;;
        --tenant=*) # required
            tenant="${i#*=}"
            shift
            ;;
        --subproject=*) # required
            subproject="${i#*=}"
            shift
            ;;
        --disable-ssl-verify)
            ssl_verify="false"
            shift
            ;;
        *)
            echo "unknown option: $i"
            exit 1
            ;;
    esac
done

# required parameters
if [[ -z "${service_url}" || -z "${service_key}" || -z "${idtoken}" || -z "${tenant}" || -z "${subproject}" || -z "${provider}" ]]; then
    echo "[usage] ./run_regression_tests.sh --service-url= --service-key= --cloud-provider= --idtoken= --tenant= --subproject="
    exit 1
fi

# set ssl verification option
if [ -z "${ssl_verify}" ]; then
    ssl_verify="true"
fi

# set the mount volume if not set as input argument
if [ -z "${mnt_volume}" ]; then
    mnt_volume="$(pwd)"
fi
cd ${mnt_volume}

# create temporary configuration for unit test
cp sdlib/config.yaml config_original.yaml
echo "seistore:" > sdlib/config.yaml
echo "    service: '{\"${provider}\": {\"env\" : {\"url\": \"${service_url}\", \"appkey\": \"${service_key}\", \"ssl_verify\": ${ssl_verify}}}}'" >> sdlib/config.yaml
echo "auth_provider:" >> sdlib/config.yaml
echo "    default: \"oauth2\"" >> sdlib/config.yaml

# pytest fetches a stoken when a service account secret key is passed.
pytest test/e2e --idtoken=${idtoken} --sdpath=sd://${tenant}/${subproject} --timeout=300 -s
exit_status=$?

# restore configuration and clear temporary files
cp config_original.yaml sdlib/config.yaml
rm config_original.yaml
if [ $exit_status -ne 0 ]; then exit 1; fi
