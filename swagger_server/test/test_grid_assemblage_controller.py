# coding: utf-8

from __future__ import absolute_import

from swagger_server.models.assemblage import Assemblage
from swagger_server.models.error_model import ErrorModel
from . import BaseTestCase
from six import BytesIO
from flask import json


class TestGridAssemblageController(BaseTestCase):
    """ GridAssemblageController integration test stubs """

    def test_grid(self):
        """
        Test case for grid

        Gridded assemblage data
        """
        query_string = [('agebound', 'agebound_example'),
                        ('agebin', 'agebin_example'),
                        ('ageunit', 'ageunit_example'),
                        ('bbox', 'bbox_example'),
                        ('spatialbin', 'spatialbin_example'),
                        ('varunit', 'varunit_example'),
                        ('presence', true)]
        response = self.client.open('/api_v1/grid',
                                    method='GET',
                                    content_type='application/json',
                                    query_string=query_string)
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
