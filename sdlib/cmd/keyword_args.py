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


class KeywordArguments():
    """ Object to hold the keyword arguments.
    Any argument has None as default
    """

    def __getattr__(self, attr):
        """ If attribute doesn't exist return None
        __getattr__ is called when __getattribute__ raises AttributeError
        """
        setattr(self, attr, None)  # add this attrib
        return getattr(self, attr)  # return its value
