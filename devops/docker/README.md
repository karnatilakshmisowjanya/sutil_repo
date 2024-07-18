# How to use

## Prerequisites

- Docker

## Prepare image

### Pull image

If you don't have a tar file with container, you can pull image directly from container registry by executing next command:

```bash
docker pull community.opengroup.org:5555/osdu/platform/domain-data-mgmt-services/seismic/seismic-dms-suite/seismic-store-sdutil/seismic-store-sdutil
```

Please notice that community.opengroup.org:5555/osdu/platform/domain-data-mgmt-services/seismic/seismic-dms-suite/seismic-store-sdutil/seismic-store-sdutil is the image tag.

### Load image

If you have a tar file with container, you can load container using next command:

```bash
docker load some_tar_file.tar.gz
```

Please notice this command will tell the image tag

## Run image

1. Execute next command:

```bash
docker run --rm -it IMAGE_TAG
```

2. Start using sdutil as usual

**Please note that in container sdutil always needs to have idtoken provided as parameter**