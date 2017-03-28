# coding: utf-8

from __future__ import absolute_import

from swagger_server.models.agebasis import Agebasis
from swagger_server.models.error_model import ErrorModel
from . import BaseTestCase
from six import BytesIO
from flask import json


class TestAgeBasisController(BaseTestCase):
    """ AgeBasisController integration test stubs """

    def test_age(self):
        """
        Test case for age

        Generation method of age estimates for the occurrence or site
        """
        query_string = [('occid', 56),
                        ('siteid', 56)]
        response = self.client.open('/api_v1/age',
                                    method='GET',
                                    content_type='application/json',
                                    query_string=query_string)
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
