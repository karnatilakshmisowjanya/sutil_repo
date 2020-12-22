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


import sys
import os

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                    os.path.abspath(__file__)))))

from sdlib.shared.utils import Utils

from test.utest import SdUtilTestCase


class TestUtils(SdUtilTestCase):
    def test_isValidEmail(self):
        self.assertTrue(Utils.isValidEmail('user@domain.com'))
        self.assertFalse(Utils.isValidEmail('user@domain'))
        self.assertFalse(Utils.isValidEmail('userdomain@'))
        self.assertFalse(Utils.isValidEmail('user'))

    def test_isSDPath(self):
        self.assertTrue(Utils.isSDPath('sd://tnx01/spx01/a/b/c/dsx01'))
        self.assertFalse(Utils.isSDPath('sdx://tnx01/spx01/a/b/c/dsx01'))
        self.assertFalse(Utils.isSDPath('gs://tnx01/spx01/a/b/c/dsx01'))

    def test_isTenant(self):
        self.assertTrue(Utils.isTenant('sd://tnx01///'))
        self.assertFalse(Utils.isTenant('sd://tnx01/spx01'))
        self.assertFalse(Utils.isTenant('sd://tnx01/spx01/a/b/c/dsx01'))
        self.assertFalse(Utils.isTenant('sdx://tnx01'))

    def test_isSubProject(self):
        self.assertTrue(Utils.isSubProject('sd://tnx01/spx01///'))
        self.assertFalse(Utils.isSubProject('sd://tnx01'))
        self.assertFalse(Utils.isSubProject('sd://tnx01/spx01/a/b/c/dsx01'))
        self.assertFalse(Utils.isSubProject('sdx://tnx01/spx01'))

    def test_isDatasetPath(self):
        self.assertTrue(Utils.isDatasetPath('sd://tnx01/spx01/a/b/c/dsx01///'))
        self.assertFalse(Utils.isDatasetPath('sd://'))
        self.assertFalse(Utils.isDatasetPath('sd://tnx01'))
        self.assertFalse(Utils.isDatasetPath('sd://tnx01/spx01'))
        self.assertFalse(Utils.isDatasetPath('sdx://tnx01/spx01/a/b/c/dsx01'))

    def test_getTenant(self):
        self.assertEqual(Utils.getTenant('sd://tnx01/spx01/a/b/c/dsx01///'), 'tnx01')
        self.assertEqual(Utils.getTenant('sdx://tnx01/spx01/a/b/c/dsx01'), None)
        self.assertEqual(Utils.getTenant('sd://'), None)

    def test_getSubproject(self):
        self.assertEqual(Utils.getSubproject('sd://tnx01/spx01/a/b/c/dsx01///'), 'spx01')
        self.assertEqual(Utils.getSubproject('sdx://tnx01/spx01/a/b/c/dsx01'), None)
        self.assertEqual(Utils.getSubproject('sd://'), None)

    def test_isValidName(self):
        self.assertTrue(Utils.isValidName('abc'))
        self.assertFalse(Utils.isValidName('a'))
        self.assertFalse(Utils.isValidName('a&'))
        self.assertFalse(Utils.isValidName('-abc'))
        self.assertFalse(Utils.isValidName('abc-'))
        self.assertFalse(Utils.isValidName('ab--cd'))
        self.assertFalse(Utils.isValidName('ab__cd'))
        self.assertFalse(Utils.isValidName('abgooglecd'))
    
    def test_SDPath2UrlEncode(self):
        self.assertEqual(Utils.SDPath2UrlEncode('sd://tnx01/spx01/a/b/c/dsx01'), 'tnx01/spx01/a%2Fb%2Fc/dsx01')
        self.assertEqual(Utils.SDPath2UrlEncode('sdx://tnx01/spx01/a/b/c/dsx01'), '')
        self.assertEqual(Utils.SDPath2UrlEncode('sd://'), '')
        self.assertEqual(Utils.SDPath2UrlEncode('sd://tnx01/spx01'), 'tnx01/spx01')
        self.assertEqual(Utils.SDPath2UrlEncode('sd://tnx01/spx01/dsx01'), 'tnx01/spx01/%2F/dsx01')

    def test_sizeof_fmt(self):
        self.assertEqual(Utils.sizeof_fmt(123), '123.0 B')
        self.assertEqual(Utils.sizeof_fmt(1025), '1.0 KB')
        self.assertEqual(Utils.sizeof_fmt(1204*10000000000000000000000), '10.0 YB')
