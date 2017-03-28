# coding: utf-8

from __future__ import absolute_import

from swagger_server.models.error_model import ErrorModel
from swagger_server.models.site import Site
from . import BaseTestCase
from six import BytesIO
from flask import json


class TestSiteController(BaseTestCase):
    """ SiteController integration test stubs """

    def test_site(self):
        """
        Test case for site

        Sample sites or localities
        """
        query_string = [('occid', 56),
                        ('bbox', 'bbox_example'),
                        ('minage', 1.2),
                        ('maxage', 1.2),
                        ('agescale', 'agescale_example'),
                        ('timerule', 'timerule_example'),
                        ('taxon', 'taxon_example'),
                        ('includelower', true)]
        response = self.client.open('/api_v1/site',
                                    method='GET',
                                    content_type='application/json',
                                    query_string=query_string)
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
