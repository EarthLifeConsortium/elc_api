# coding: utf-8

from __future__ import absolute_import

from swagger_server.models.error_model import ErrorModel
from swagger_server.models.occurrence import Occurrence
from . import BaseTestCase
from six import BytesIO
from flask import json


class TestOccurrenceController(BaseTestCase):
    """ OccurrenceController integration test stubs """

    def test_occ(self):
        """
        Test case for occ

        Fossil occurrences in a specific place and time
        """
        query_string = [('bbox', 'bbox_example'),
                        ('minage', 1.2),
                        ('maxage', 1.2),
                        ('agescale', 'agescale_example'),
                        ('timerule', 'timerule_example'),
                        ('taxon', 'taxon_example'),
                        ('includelower', true),
                        ('limit', 56),
                        ('offset', 56),
                        ('show', 'show_example')]
        response = self.client.open('/api_v1/occ',
                                    method='GET',
                                    content_type='application/json',
                                    query_string=query_string)
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
