ARG run_tests=false
ARG E2E_HOSTNAME=localhost
ARG SDMS_PREFIX="/seistore-svc/api/v3"
ARG E2E_TENANT=mytenant
ARG E2E_SUBPROJECT=mysubproject
ARG svctoken=mytoken

FROM python:3.10 as development
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
RUN if [ "${run_tests}" != "false" ]; then \
    pip install -r test/requirements.txt \
    chmod +x devops/scripts/run_unit_tests.sh \
    ./devops/scripts/run_unit_tests.sh \
  fi
RUN mkdir -p dist \
  rm -rf dist/*
RUN version_major=3 \
  version_minor=0 \
  PACKAGE_VERSION=${version_major}.${version_minor}.$CI_PIPELINE_IID \
  echo $PACKAGE_VERSION > .version
RUN cp -r LICENSE NOTICE README.md requirements.txt sdlib sdutil sdutil.py .version dist
RUN if [ "${run_tests}" != "false" ]; then \
    pip install -r test/requirements.txt \
    chmod +x ./devops/scripts/run_regression_tests.sh \
    ./devops/scripts/run_regression_tests.sh --cloud-provider=azure --service-url="https://${E2E_HOSTNAME}${SDMS_PREFIX}" --service-env=gitlab --tenant="${E2E_TENANT}" --subproject="${E2E_SUBPROJECT}" --idtoken="${svctoken}"
  fi

FROM python:3.10 as release
WORKDIR /app
COPY --from=development /app/dist /app
RUN ls
ENTRYPOINT ["/bin/bash"]