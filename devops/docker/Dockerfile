ARG python_version=latest

FROM python:${python_version} as development
ARG arg_run_tests=false
ARG arg_E2E_HOSTNAME=localhost
ARG arg_SDMS_PREFIX="/seistore-svc/api/v3"
ARG arg_E2E_TENANT=mytenant
ARG arg_E2E_SUBPROJECT=mysubproject
ARG arg_AZURE_TENANT_ID
ARG arg_AZURE_AD_APP_RESOURCE_ID
ARG arg_INTEGRATION_TESTER
ARG arg_AZURE_TESTER_SERVICEPRINCIPAL_SECRET

ENV run_tests=${arg_run_tests}
ENV E2E_HOSTNAME=${arg_E2E_HOSTNAME}
ENV SDMS_PREFIX=${arg_SDMS_PREFIX}
ENV E2E_TENANT=${arg_E2E_TENANT}
ENV E2E_SUBPROJECT=${arg_E2E_SUBPROJECT}
ENV AZURE_TENANT_ID=${arg_AZURE_TENANT_ID}
ENV AZURE_AD_APP_RESOURCE_ID=${arg_AZURE_AD_APP_RESOURCE_ID}
ENV INTEGRATION_TESTER=${arg_INTEGRATION_TESTER}
ENV AZURE_TESTER_SERVICEPRINCIPAL_SECRET=${arg_AZURE_TESTER_SERVICEPRINCIPAL_SECRET}

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
RUN if [ "${run_tests}" != "false" ]; then \
    pip install -r test/requirements.txt; \
  fi
RUN if [ "${run_tests}" != "false" ]; then \
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
RUN if [ "${run_tests}" != "false" ]; then \
    echo "host: ${E2E_HOSTNAME}"; \
    echo "sdms prefix: ${SDMS_PREFIX}"; \
    echo "tenant: ${E2E_TENANT}"; \
    echo "subproject: ${E2E_SUBPROJECT}"; \
    pip install msal; \
    export svctoken=$(python ${CI_PROJECT_DIR}/devops/scripts/azure_jwt_client.py); \
    chmod +x ./devops/scripts/run_regression_tests.sh; \
    ./devops/scripts/run_regression_tests.sh --cloud-provider=azure --service-url="https://${E2E_HOSTNAME}${SDMS_PREFIX}" --service-env=gitlab --tenant="${E2E_TENANT}" --subproject="${E2E_SUBPROJECT}" --idtoken=${svctoken}; \
  fi

FROM python:3.10 as release
WORKDIR /app
COPY --from=development /app/dist /app
RUN ls
ENTRYPOINT ["/bin/bash"]