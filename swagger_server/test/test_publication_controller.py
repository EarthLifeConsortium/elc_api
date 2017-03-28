# coding: utf-8

from __future__ import absolute_import

from swagger_server.models.error_model import ErrorModel
from swagger_server.models.publication import Publication
from . import BaseTestCase
from six import BytesIO
from flask import json


class TestPublicationController(BaseTestCase):
    """ PublicationController integration test stubs """

    def test_pub(self):
        """
        Test case for pub

        Scientific publications associated with sites or occurrences
        """
        query_string = [('occid', 56),
                        ('siteid', 56),
                        ('format', 'format_example')]
        response = self.client.open('/api_v1/pub',
                                    method='GET',
                                    content_type='application/json',
                                    query_string=query_string)
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
