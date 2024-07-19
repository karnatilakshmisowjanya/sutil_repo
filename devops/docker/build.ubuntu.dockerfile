FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

# install required build tools via packet manager
RUN apt-get -y update && apt-get -y install python3-pip && python -m pip3 install --upgrade pip

# temporary working directory
WORKDIR /tmp

# install required dependencies
COPY requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt
RUN rm -f requirements.txt

# install tests required dependencies
COPY test/requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt
RUN rm -f requirements.txt

# finalize
WORKDIR /
RUN rm -rf /var/lib/apt/lists/*