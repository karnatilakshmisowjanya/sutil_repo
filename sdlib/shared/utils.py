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


import os
import re
from sdlib.shared.config import Config
from urllib.parse import quote

class Utils(object):

    @staticmethod
    def isSDPath(sdpath):
        return str(sdpath).startswith(Config.SDPATH_PREFIX)

    @staticmethod
    def isTenant(sdpath):

        sdpath = str(sdpath)

        if Utils.isSDPath(sdpath) is False:
            return False

        sdpath = sdpath[len(Config.SDPATH_PREFIX):]
        if not sdpath:
            return False

        while sdpath[-1] == '/':
            sdpath = sdpath[:-1]

        return sdpath.count('/') == 0 and Utils.isValidName(sdpath)

    @staticmethod
    def isSubProject(sdpath):

        sdpath = str(sdpath)

        if Utils.isSDPath(sdpath) is False:
            return False

        sdpath = sdpath[len(Config.SDPATH_PREFIX):]
        if not sdpath:
            return False

        while sdpath[-1] == '/':
            sdpath = sdpath[:-1]

        return (sdpath.count('/') == 1
                and Utils.isValidName(sdpath.split('/')[0])
                and Utils.isValidName(sdpath.split('/')[1]))

    @staticmethod
    def isDatasetPath(sdpath):

        sdpath = str(sdpath)

        if Utils.isSDPath(sdpath) is False:
            return False

        sdpath = sdpath[len(Config.SDPATH_PREFIX):]

        if not sdpath:
            return False

        while sdpath[-1] == '/':
            sdpath = sdpath[:-1]

        if sdpath.count('/') < 2:
            return False

        sdpath = sdpath[sdpath.find('/')+1:]
        sdpath = sdpath[sdpath.find('/')+1:]

        return len(sdpath) != 0

    @staticmethod
    def getTenant(sdpath):

        sdpath = str(sdpath)

        if Utils.isSDPath(sdpath) is False:
            return None

        sdpath = sdpath[len(Config.SDPATH_PREFIX):]

        if not sdpath:
            return None

        while sdpath[-1] == '/':
            sdpath = sdpath[:-1]

        return sdpath.split('/')[0]

    @staticmethod
    def getSubproject(sdpath):

        sdpath = str(sdpath)

        if Utils.isSDPath(sdpath) is False:
            return None

        sdpath = sdpath[len(Config.SDPATH_PREFIX):]

        if not sdpath:
            return None

        while sdpath[-1] == '/':
            sdpath = sdpath[:-1]

        tmp = sdpath.split('/')

        return tmp[1] if len(tmp) > 1 else None

    @staticmethod
    def isValidName(sdpath):

        sdpath = str(sdpath)

        if len(sdpath) < 2:
            return False

        if not re.match(r"^([a-z0-9_-])+$", sdpath):
            return False

        if sdpath[0] == '-' or sdpath[0] == '_':
            return False

        if sdpath[-1] == '-' or sdpath[-1] == '_':
            return False

        if sdpath.find("--") != - 1 or sdpath.find("-_") != - 1:
            return False

        if sdpath.find("__") != - 1 or sdpath.find("_-") != - 1:
            return False

        # do not use the keword 'google' in a seistore item name
        if sdpath.find("google") != - 1:
            return False

        return True

    @staticmethod
    def SDPath2UrlEncode(sdpath):

        sdpath = str(sdpath)

        if 'sd://' not in sdpath:
            return ''

        sdpath = str(sdpath.replace("sd://", ""))

        if sdpath.count('/') == 0:
            return sdpath

        splitpath = sdpath.split('/')

        if sdpath.count('/') == 1:
            return splitpath[0] + '/' + splitpath[1]

        names = ['', '', '', '']
        names[0] = splitpath[0]
        names[1] = splitpath[1]
        names[3] = quote(splitpath[-1], safe='')
        splitpath = splitpath[2:-1]
        if splitpath:
            names[2] += ('%2F'.join(map(str, splitpath)))
        else:
            names[2] = '%2F'
        return '/'.join(names)

    @staticmethod
    def sizeof_fmt(num, suffix='B'):
        for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
            if abs(num) < 1024.0:
                return "%3.1f %s%s" % (num, unit, suffix)
            num /= 1024.0
        return "%.1f %s%s" % (num, 'Y', suffix)

    @staticmethod
    def getFileName(filePath):
        fileName = filePath
        if ("/" in fileName or "\\" in fileName):
            fileName = os.path.split(fileName)[-1]
        return fileName
