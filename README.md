# Seismic Store SDUTIL

A command line python utility designed to easily with seismic store.

Seismic store is a cloud-based solution designed to store and manage datasets of any size in the cloud by enabling a secure way to access them through a scoped authorization mechanism. Seismic Store overcomes the object size limitations imposed by a cloud provider, by managing generic datasets as multi independent objects and, therefore, provides a generic, reliable and a better performed solution to handle data on a cloud storage.

The **sdutil** is an intuitive command line utility tool to interact with seismic store and perform some basic operations like upload or download datasets to or from seismic store, manage users, list folders content and more.

- [Seismic Store SDUTIL](#seismic-store-sdutil)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Seistore Resources](#seistore-resources)
  - [Subprojects](#subprojects)
  - [Users Management](#users-management)
  - [Usage Examples](#usage-examples)
  - [Utility Testing](#utility-testing)
  - [FAQ](#faq)

## Prerequisites

Windows

- [64-bit Python 3.8.3](https://www.python.org/ftp/python/3.8.3/python-3.8.3-amd64.exe)
- [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)

Linux

- [64-bit Python 3.8.3](https://www.python.org/ftp/python/3.8.3/Python-3.8.3.tgz)

Unix

- [64-bit Python 3.8.3](https://www.python.org/ftp/python/3.8.3/Python-3.8.3.tgz)
- [Apple Xcode C++ Build Tools]

Other requirements are addressed in the INSTALLATION section below.

## Installation

The utility is released as a zip package:

unzip the utility to a folder

```sh
unzip sdutil-1.0.0
```

The utility requires additional modules noted in [requirements.txt](requirements.txt). You could either install the modules as is or install them in virtualenv to keep your host clean from package conflicts. if you don't want to install them in a virtual environment please jump directly to the step 3.

```sh
# check if virtualenv is already installed
virtualenv --version

# if not install it via pip
pip install virtualenv

# create a virtual environment for sdutil
virtualenv sdutilenv

# activate the virtual environemnt
Windows:    sdutilenv/Scripts/activate  
Linux:      source sdutilenv/bin/activate
```

install required dependencies:

```bash
# run it from the extracted sdutil folder
pip install -r requirements.txt
```

## Usage

Run the utility from the extracted utility folder by typing:

```sh
python sdutil
```

If no arguments are specified, this menu will be displayed:

```code
Seismic Store Utility

> python sdutil [command]

available commands:

 * auth    : authentication utilities
 * unlock  : remove a lock on a seismic store dataset
 * version : print the sdutil version
 * rm      : delete a subproject or a space separated list of datasets
 * mv      : move a dataset in seismic store
 * config  : manage the utility configuration
 * mk      : create a subproject resource
 * cp      : copy data to(upload)/from(download)/in(copy) seismic store
 * stat    : print information like size, creation date, legal tag(admin) for a space separated list of tenants, subprojects or datasets
 * patch   : patch a seismic store subproject or dataset
 * app     : application authorization utilities
 * ls      : list subprojects and datasets
 * user    : user authorization utilities
```

At first usage time, the utility required to be initialized by invoking the sdutil config init command.

```sh
python sdutil config init
```

Before start using the utility and perform any operation, you must login into the system. By running the following login command, sdutil will open a sign-in page in a web browser.

```sh
python sdutil auth login
```

Once you have successfully logged in, your credentials will be valid for a week. You don't need to login again unless the credentials expired (after 1 week), in this case the system will require you to login again.

## Seistore Resources

Before start using the system it's important to understand how resources are addressed in seismic store. There are 3 different types of resources managed by seismic store:

- `Tenant Project`: the main project. This is the first section of the seismic store path

- `Subproject`: the working sub-project, directly linked under the main tenant project. This is the second section of the seismic store path.

- `Dataset`: the seismic store dataset entity. This is the third and last section of the seismic store path. The Dataset resource can be specified by using the form `path/dataset_name` where `path` is optional and have the same meaning of a directory in a generic file-system and `dataset_name` is the name of the dataset entity.

The seismic store uri is a string used to uniquely address a resource in the system and can be obtained by appending the prefix `sd://` before the required resource path:

```code
sd://<tenant>/<subproject>/<path>*/<dataset>
```

For example if we have a dataset `results.segy` stored in the directory structure `qadata/ustest` in the `carbon` subproject under the `gtc` tenant project, then the corresponding sdpath will be:

```code
sd://gtc/carbon/qadata/ustest/results.segy
```

Every resource can be address by using the corresponding sdpath section

```code
Tenant: sd://gtc
Subproject: sd://gtc/carbon
Dataset: sd://gtc/carbon/qadata/ustest/results.segy
```

## Subprojects

A subproject in Seismic Store is a working unit where datasets can be saved. The system can handles multiple subprojects under a tenant project.

A subproject resource can be created by a `Tenant Admin Only` with the following sdutil command:

```code
> python sdutil mk python sdutil mk *sdpath *admin@email *legaltag (options)

  create a new subproject resource in the seismic store. user can interactively
  set the storage class for the subproject. only tenant admins are allowed to create subprojects.

  *sdpath       : the seismic store subproject path. sd://<tenant>/<subproject>
  *admin@email  : the email of the user to be set as the subproject admin
  *legaltag     : the default legal tag for the created subproject

  (options)     | --idtoken=<token> pass the credential token to use, rather than generating a new one
```

## Users Management

To be able to use seismic store, a user must be registered/added to at least a subproject resource with a role that define his access level. Seismic Store support three different roles scoped at subproject level:

- **admin**: read/write/list/delete access + users management.
- **editor**: read/write/list/delete access
- **viewer**: read/list access

A user can be register by a `Subproject Admin Only` with the following sdutil command:

```code
> python sdutil user [ *add | *list | *remove | *roles ] (options)

  *add       $ python sdutil user add [user@email] [sdpath] [role]*
               add a user to a subproject resource

               [user@email]  : email of the user to add
               [sdpath]      : seismic store subproject path, sd://<tenant>/<subproject>
               [role]        : user role [admin|editor|viewer]
```

## Usage Examples

An example on how to use sdutil to manage datasets with seismic store. For this example we will use sd://gtc/carbon as subproject resource

```bash

# create a new file
echo "My Test Data" > data1.txt

# upload the created file to seismic store
./sdutil cp data1.txt sd://gtc/carbon/test/mydata/data.txt

# list the content of the seismic store subproject
./sdutil ls sd://gtc/carbon/test/mydata/  (display: data.txt)
./sdutil ls sd://gtc                      (display: carbon)
./sdutil ls sd://gtc/carbon               (display: test/)
./sdutil ls sd://gtc/carbon/test          (display: data/)

# download the file from seismic store:
./sdutil cp sd://gtc/carbon/test/mydata/data.txt data2.txt

# check if file orginal file match the one downloaded from sesimic store:
diff data1.txt data2.txt
```

## Utility Testing

The test folder contains a set of integral/unit and regressions/e2e tests written for [pytest](https://docs.pytest.org/en/latest/). These tests should be executed to validate the utility funcionalities.

Requirements

  ```bash
  # install required dependencies:  
  pip install -r test/e2e/requirements.txt
  ```

Integral/Unit tests

  ```bash
  # run integral/unit test
  ./devops/scripts/run_unit_tests.sh

  # test execution paramaters
  --mnt-volume = sdapi root dir (default=".")
  ```

Regression tests

  ```bash
  # run integral/unit test
  ./devops/scripts/run_regression_tests.sh --cloud-provider= --service-url= --service-key= --idtoken= --tenant= --subproject=

  # test execution paramaters
  --mnt-volume = sdapi root dir (default=".")
  --disable-ssl-verify (to disable ssl verification)
  ```

## FAQ

How can I generate a new utility command?

run the [command generation script](./command_gen.py) to automatically generate the base infrastracture for integrate new command in the sdutil utility. A folder with the command infrastrcture will be created in sdlib/cmd/new_command_name

```bash
./scripts/command_gen.py new_command_name
```

How can I delete all files in a directory?

```shell
./sdutil ls -lr sd://tenant/subproject/your/folder/here | xargs -r ./sdutil rm --idtoken=x.xxx.x
```

How can I generate the utility changelog?

run the [changelog script](./changelog-generator.sh) to automatically generate the utility changelog

```bash
./scripts/changelog_gen.sh
```
