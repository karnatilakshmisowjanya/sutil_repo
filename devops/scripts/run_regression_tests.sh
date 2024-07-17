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
        --service-env=*) # required
            service_env="${i#*=}"
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
        --legaltag=*) # required
            legaltag="${i#*=}"
            shift
            ;;
        --legaltag02=*) # required
            legaltag02="${i#*=}"
            shift
            ;;
        --admin=*) # required
            admin="${i#*=}"
            shift
            ;;
        --acl-admin=*) # required
            acl_admin="${i#*=}"
            shift
            ;;
        --acl-viewer=*) # required
            acl_viewer="${i#*=}"
            shift
            ;;
        --disable-ssl-verify)
            ssl_verify="true"
            shift
            ;;
        *)
            echo "unknown option: $i"
            exit 1
            ;;
    esac
done

# required parameters
if [[ -z "${service_url}" || -z "${service_env}" || -z "${idtoken}" || -z "${tenant}" || -z "${subproject}" || -z "${legaltag}" || -z "${legaltag02}" || -z "${admin}" || -z "${acl_admin}" || -z "${acl_viewer}" || -z "${provider}" ]]; then
    echo "[usage] ./run_regression_tests.sh --cloud-provider= --service-url= --service-env= --tenant= --subproject= --legaltag= --admin= --idtoken="
    echo "service-url: ${service_url} \n" 
    echo "service-env: ${service_env} \n"
    echo "tenant: ${tenant} \n"
    echo "subproject: ${subproject} \n"
    echo "legaltag: ${legaltag} \n"
    echo "legaltag02: ${legaltag02} \n"
    echo "admin: ${admin} \n"
    echo "acl-admin: ${acl_admin} \n"
    echo "acl-viewer: ${acl_viewer} \n"
    if [[ -z "${idtoken}" ]]; then echo "idtoken is not provided"; fi
    exit 1
fi

# set ssl verification option
if [ -z "${ssl_verify}" ]; then
    ssl_verify="false"
fi

# set the mount volume if not set as input argument
if [ -z "${mnt_volume}" ]; then
    mnt_volume="$(pwd)"
fi
cd ${mnt_volume}

# create temporary configuration for unit test
FILE1=sdlib/config.yaml
if test -f "$FILE1"; then
    cp sdlib/config.yaml config_original.yaml
fi

cat /dev/null > sdlib/config.yaml
echo "seistore:" > sdlib/config.yaml
echo "  service: '{
    \"${provider}\":{
      \"${service_env}\":{
        \"url\": \"${service_url}\",
        \"ssl_verify\": ${ssl_verify}}}}'" >> sdlib/config.yaml
echo "auth_provider:" >> sdlib/config.yaml
echo "  default: null" >> sdlib/config.yaml

# pytest fetches a stoken when a service account secret key is passed.
pytest --forked -v --log-format="%(asctime)s %(levelname)s %(message)s" --log-date-format="%Y-%m-%d %H:%M:%S" --timeout=300 \
    test/e2e --idtoken=${idtoken} --sdpath=sd://${tenant}/${subproject} --admin=${admin} --legaltag=${legaltag} --legaltag02=${legaltag02} --acl_admin=${acl_admin} --acl_viewer=${acl_viewer}
exit_status=$?

# restore configuration and clear temporary files
FILE2=config_original.yaml
if test -f "$FILE2"; then
    cp config_original.yaml sdlib/config.yaml
    rm config_original.yaml
else 
    rm sdlib/config.yaml
fi
if [ $exit_status -ne 0 ]; then exit 1; fi
