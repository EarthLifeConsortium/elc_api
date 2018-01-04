# coding: utf-8

from __future__ import absolute_import

from swagger_server.models.error_model import ErrorModel
from swagger_server.models.reference import Reference
from . import BaseTestCase
from six import BytesIO
from flask import json


class TestReferenceController(BaseTestCase):
    """ ReferenceController integration test stubs """

    def test_ref(self):
        """
        Test case for ref

        Scientific references associated with locales (datasets or collections) and occurrences
        """
        query_string = [('idnumbers', 'idnumbers_example'),
                        ('output', 'output_example')]
        response = self.client.open('/api_v1/ref',
                                    method='GET',
                                    content_type='application/json',
                                    query_string=query_string)
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
