# How to use

## Prerequisites

- Docker

## Pull image

Execute next command:

´´´Bash
docker pull community.opengroup.org:5555/osdu/platform/domain-data-mgmt-services/seismic/seismic-dms-suite/seismic-store-sdutil/seismic-store-sdutil
´´´

## Run image

1. Execute next command:

´´´Bash
docker run --rm -it community.opengroup.org:5555/osdu/platform/domain-data-mgmt-services/seismic/seismic-dms-suite/seismic-store-sdutil/seismic-store-sdutil
´´´

2. Start using sdutil as usual

**Please note that in container sdutil always needs to have idtoken provided as parameter**