# This program is free software; you can redistribute it and/or modify
# it under the terms of the (LGPL) GNU Lesser General Public License as
# published by the Free Software Foundation; either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library Lesser General Public License for more details at
# ( http://www.gnu.org/licenses/lgpl.html ).
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
# written by: Jeff Ortel ( jortel@redhat.com )
import os
import sys

from suds import OverloadedMethodNotMatchingError, OverloadedMethodWithPositionalArgumentsError, MethodNotFound
from suds.client import Client

sys.path.insert(0, '../')
import unittest
from unittest import TestCase
from tests import setup_logging

setup_logging()


class FactoryTest(TestCase):
    def setUp(self):
        super().setUp()
        url = 'file://' + os.path.abspath("test_overload_DuckService.wsdl")
        self.client = Client(url)
        print(self.client)
        self.service = self.client.service
        self.factory = self.client.factory
        self.methods = self.client.wsdl.services[0].ports[0].methods

    def testSimpleObjectAttr(self):
        obj = self.factory.T_KeyValuePair(Key="key1",
                                          Value="value1")

        assert obj.Key == "key1"
        assert obj.Value == "value1"

    def testSimpleObjectItem(self):
        obj = self.factory['T_KeyValuePair'](Key="key1",
                                             Value="value1")

        assert obj.Key == "key1"
        assert obj.Value == "value1"

    def testDefaultAttr(self):
        obj = self.factory.T_KeyValuePair()

        assert obj.Key is None
        assert obj.Value is None

    def testInvalidAttr(self):
        try:
            self.factory.T_KeyValuePair(Invalid=True)
            self.fail("Invalid key should raise an exception")
        except AttributeError:
            pass


if __name__ == '__main__':
    unittest.main()
