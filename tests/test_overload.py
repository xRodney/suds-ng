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
import urllib

from suds.client import Client

sys.path.insert(0, '../')
import unittest
from suds.xsd.sxbuiltin import XDate, XTime, XDateTime
from suds.sax.date import Timezone
from unittest import TestCase
from tests import setup_logging
import datetime as dt

setup_logging()

SUBMIT_RESPONSE = """<?xml version="1.0" encoding="UTF-8"?>
<SOAP-ENV:Envelope xmlns:ns0="http://schemas.xmlsoap.org/soap/encoding/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:ns2="http://schemas.xmlsoap.org/soap/envelope/" xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ns1="http://www.example.com/donald" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
   <SOAP-ENV:Header/>
   <ns2:Body>
      <ns1:Disco.SubmitResponse/>
   </ns2:Body>
</SOAP-ENV:Envelope>
"""

def check_real_method(real_method_object, expected_name, expected_output_part_names=[]):
    assert real_method_object.name == expected_name
    output_parts = real_method_object.soap.output.body.parts
    output_part_names = [part.name for part in output_parts]
    assert output_part_names == expected_output_part_names

class OverloadTest(TestCase):

    def testOverload(self):
        url = 'file://' + os.path.abspath("test_overload_DuckService.wsdl")
        client = Client(url)
        print(client)
        service = client.service

        methods = client.wsdl.services[0].ports[0].methods
        assert len(methods) == 4
        job_submit_method = methods["Disco.Submit"]
        job_list_method = methods["Disco.List"]

        assert len(job_submit_method) == 3
        assert len(job_list_method) == 1

        [m1, m2, m3] = job_submit_method

        assert m1 is not m2

        assert m1.soap != m2.soap
        assert m2.soap != m3.soap
        assert m3.soap != m1.soap

        sim = {"reply": SUBMIT_RESPONSE}


        call = getattr(service, "Disco.List")
        assert len(call.methods) == 1
        assert call.method is not None

        overloaded_call = getattr(service, "Disco.Submit")
        assert len(overloaded_call.methods) == 3
        assert overloaded_call.method is None


        call = overloaded_call[2]
        check_real_method(call.method, "Disco.Submit", ["MalformedJob", "InvalidJob", "Msg"])
        call(__inject=sim)
        assert "Disco.Submit/>" in str(client.last_sent())

        call = overloaded_call[1]
        call(__inject=sim)
        check_real_method(call.method, "Disco.Submit", ["invalidJob", "resendList"])
        assert "Disco.Submit/>" in str(client.last_sent())

        call = overloaded_call[0]
        call(__inject=sim)
        check_real_method(call.method, "Disco.Submit", ["resendList"])
        assert "Disco.Submit/>" in str(client.last_sent())

if __name__ == '__main__':
    unittest.main()
