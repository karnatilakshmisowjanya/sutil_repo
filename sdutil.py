#!/usr/bin/env python
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


"""Wrapper module for running gslib.__main__.main() from the command line."""

from __future__ import print_function

import os
import sys


def OutputAndExit(message):
    sys.stderr.write('%s\n' % message)
    sys.exit(1)


SDUTIL_DIR = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
if not SDUTIL_DIR:
    OutputAndExit('Unable to determine where sdutil is installed.'
                  ' Sorry, cannot run correctly without this.\n')


def RunMain():
    import sdlib.__main__
    sys.exit(sdlib.__main__.main())


if __name__ == '__main__':
    RunMain()
