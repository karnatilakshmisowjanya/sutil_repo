#-------------------------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See https://go.microsoft.com/fwlink/?linkid=2090316 for license information.
#-------------------------------------------------------------------------------------------------------------

# To fully customize the contents of this image, use the following Dockerfile instead:
# https://github.com/microsoft/vscode-dev-containers/tree/v0.117.1/containers/python-3/.devcontainer/base.Dockerfile
ARG VARIANT="3.8"
FROM mcr.microsoft.com/vscode/devcontainers/python:0-${VARIANT}

# prevent operating as root
USER vscode

# init virtualenv as the default python interpreter
ENV VIRTUAL_ENV="/usr/local/py-utils/venvs/virtualenv"
ARG VARIANT
RUN virtualenv --python=/usr/local/bin/python${VARIANT} $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# copy dependency sync script for session and package management
COPY ./.devcontainer/sync_deps.py /workspaces/session/post-create/

# elevate permissions for session and package management
RUN sudo chmod o+w -R /workspaces/

# install latest package manager(s)
RUN python3 -m pip install --upgrade pip

# install requirements into virtualenv layer of dev image
COPY requirements.txt /workspaces/session/
RUN pip --disable-pip-version-check --no-cache-dir install -r /workspaces/session/requirements.txt
