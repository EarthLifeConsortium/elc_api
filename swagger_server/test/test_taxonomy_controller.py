# coding: utf-8

from __future__ import absolute_import

from swagger_server.models.error_model import ErrorModel
from swagger_server.models.taxonomy import Taxonomy
from . import BaseTestCase
from six import BytesIO
from flask import json


class TestTaxonomyController(BaseTestCase):
    """ TaxonomyController integration test stubs """

    def test_taxon(self):
        """
        Test case for taxon

        Taxonomic information, or hierarchy
        """
        query_string = [('taxon', 'taxon_example'),
                        ('includelower', true),
                        ('hierarchy', true)]
        response = self.client.open('/api_v1/taxon',
                                    method='GET',
                                    content_type='application/json',
                                    query_string=query_string)
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
