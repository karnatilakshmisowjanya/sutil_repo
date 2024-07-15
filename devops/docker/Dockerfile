FROM python:3.10 as development
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
RUN pip install -r test/requirements.txt
RUN chmod +x devops/scripts/run_unit_tests.sh
RUN ./devops/scripts/run_unit_tests.sh
RUN mkdir -p dist
RUN rm -rf dist/*
RUN version_major=3
RUN version_minor=0
RUN PACKAGE_VERSION=${version_major}.${version_minor}.$CI_PIPELINE_IID
RUN echo $PACKAGE_VERSION > .version
RUN cp -r LICENSE NOTICE README.md requirements.txt sdlib sdutil sdutil.py .version dist
RUN ls dist
RUN chmod +x ./devops/scripts/run_regression_tests.sh


FROM python:3.10 as release
WORKDIR /app
COPY --from=development /app/dist /app
RUN ls
ENTRYPOINT ["/bin/bash"]