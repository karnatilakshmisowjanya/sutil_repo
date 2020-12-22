# -*- coding: utf-8 -*-
# Copyright 2017-2019, Schlumberger
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


class Dataset(object):
    tenant = None
    subproject = None
    path = None
    name = None
    created_by = None
    extension = None
    created_date = None
    last_modified_date = None
    objects = None
    size = None
    metadata = None
    filemetadata = None
    readonly = None
    # TODO: marked for renaming, dependent on changes to seismic store service
    gcsurl = None
    dstype = None
    legaltag = None
    sbit = None
    sbit_count = None
    seismicmeta = None
    seismicmeta_guid = None

    @classmethod
    def from_json(cls, data):
        dataset = cls()
        dataset.tenant = data['tenant']
        dataset.subproject = data['subproject']
        dataset.path = data['path']
        dataset.name = data['name']
        dataset.created_by = data['created_by']
        dataset.dstype = data.get('type', None)
        dataset.created_date = data['created_date']
        dataset.last_modified_date = data['last_modified_date']
        dataset.metadata = data.get('metadata', None)
        dataset.filemetadata = data.get('filemetadata', None)
        # TODO: marked for renaming, dependent on changes to seismic store service
        dataset.gcsurl = data['gcsurl']
        dataset.legaltag = data.get('ltag', None)
        dataset.readonly = data.get('readonly', False)
        dataset.sbit = data.get('sbit', None)
        dataset.sbit_count = data.get('sbit_count', None)
        dataset.seismicmeta = data.get('seismicmeta', None)
        dataset.seismicmeta_guid = data.get('seismicmeta_guid', None)
        return dataset
