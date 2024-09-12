# ============================================================================
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
# ============================================================================

# base image
FROM ubuntu:24.04 as development

ARG arg_run_unit_tests=false
ARG arg_run_integration_tests=false
ARG arg_E2E_HOSTNAME=localhost
ARG arg_SDMS_PREFIX="/seistore-svc/api/v3"
ARG arg_E2E_TENANT=mytenant
ARG arg_E2E_SUBPROJECT=mysubproject
ARG arg_E2E_LEGALTAG
ARG arg_E2E_LEGALTAG02
ARG arg_AZURE_AD_VALID_OID_USER1
ARG arg_ACL_OWNERS
ARG arg_ACL_VIEWERS
ARG arg_AZURE_TENANT_ID
ARG arg_AZURE_AD_APP_RESOURCE_ID
ARG arg_INTEGRATION_TESTER
ARG arg_AZURE_TESTER_SERVICEPRINCIPAL_SECRET

ENV run_unit_tests=${arg_run_unit_tests}
ENV run_integration_tests=${arg_run_integration_tests}
ENV E2E_HOSTNAME=${arg_E2E_HOSTNAME}
ENV SDMS_PREFIX=${arg_SDMS_PREFIX}
ENV E2E_TENANT=${arg_E2E_TENANT}
ENV E2E_SUBPROJECT=${arg_E2E_SUBPROJECT}
ENV E2E_LEGALTAG=${arg_E2E_LEGALTAG}
ENV E2E_LEGALTAG02=${arg_E2E_LEGALTAG02}
ENV AZURE_AD_VALID_OID_USER1=${arg_AZURE_AD_VALID_OID_USER1}
ENV ACL_OWNERS=${arg_ACL_OWNERS}  
ENV ACL_VIEWERS=${arg_ACL_VIEWERS}
ENV AZURE_TENANT_ID=${arg_AZURE_TENANT_ID}
ENV AZURE_AD_APP_RESOURCE_ID=${arg_AZURE_AD_APP_RESOURCE_ID}
ENV INTEGRATION_TESTER=${arg_INTEGRATION_TESTER}
ENV AZURE_TESTER_SERVICEPRINCIPAL_SECRET=${arg_AZURE_TESTER_SERVICEPRINCIPAL_SECRET}

WORKDIR /app
COPY . .

RUN apt-get -y update && apt-get -y install \
    python3 \
    python3-pip \
    python-is-python3

RUN echo Using: $(python --version)

RUN pip install -r requirements.txt --break-system-packages;
RUN if [ "${run_unit_tests}" != "false" ] || [ "${run_integration_tests}" != "false" ]; then \
    pip install -r test/requirements.txt --break-system-packages; \
  fi
RUN if [ "${run_unit_tests}" != "false" ]; then \
    chmod +x devops/scripts/run_unit_tests.sh; \
    ./devops/scripts/run_unit_tests.sh; \
  fi
RUN mkdir -p dist; \
  rm -rf dist/*
RUN version_major=3; \
  version_minor=0; \
  PACKAGE_VERSION=${version_major}.${version_minor}.$CI_PIPELINE_IID; \
  echo $PACKAGE_VERSION > .version
RUN cp -r LICENSE NOTICE README.md requirements.txt sdlib sdutil sdutil.py .version dist
RUN if [ "${run_integration_tests}" != "false" ]; then \
    pip install msal --break-system-packages; \
    export svctoken=$(python ./devops/scripts/azure_jwt_client.py); \
    chmod +x ./devops/scripts/run_regression_tests.sh; \
    echo "host: ${E2E_HOSTNAME}"; \
    echo "sdms prefix: ${SDMS_PREFIX}"; \
    echo "tenant: ${E2E_TENANT}"; \
    echo "subproject: ${E2E_SUBPROJECT}"; \
    echo "legaltag: ${E2E_LEGALTAG}"; \
    echo "legaltag02: ${E2E_LEGALTAG02}"; \
    echo "admin: ${AZURE_AD_VALID_OID_USER1}"; \
    echo "acl owners: ${ACL_OWNERS}"; \
    echo "acl viewers: ${ACL_VIEWERS}"; \
    ./devops/scripts/run_regression_tests.sh --cloud-provider=azure --service-url="https://${E2E_HOSTNAME}${SDMS_PREFIX}" --service-env=gitlab --tenant="${E2E_TENANT}" --subproject="${E2E_SUBPROJECT}" --legaltag="${E2E_LEGALTAG}" --legaltag02="${E2E_LEGALTAG02}" --admin="${AZURE_AD_VALID_OID_USER1}" --acl-admin="${ACL_OWNERS}" --acl-viewer="${ACL_VIEWERS}" --idtoken=${svctoken}; \
  fi

FROM ubuntu:24.04 as release
WORKDIR /app
COPY --from=development /app/dist /app
RUN pip install -r requirements.txt
ENTRYPOINT ["/bin/bash"]