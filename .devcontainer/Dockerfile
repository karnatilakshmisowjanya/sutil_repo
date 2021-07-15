ARG VARIANT="3"
FROM mcr.microsoft.com/vscode/devcontainers/python:0-${VARIANT}

USER vscode

# Temporary working directory
WORKDIR /tmp

# Install required dependencies
COPY requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt


# Install tests required dependencies
COPY test/requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt

WORKDIR /
