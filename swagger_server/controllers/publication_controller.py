import connexion
from swagger_server.models.error_model import ErrorModel
from swagger_server.models.publication import Publication
from datetime import date, datetime
from typing import List, Dict
from six import iteritems
from ..util import deserialize_date, deserialize_datetime


def pub(occid=None, siteid=None, format=None):
    """
    Scientific publications associated with sites or occurrences
    Uses unique site IDs or occurrence IDs to return the set of publications associated with a query to enable citation
    :param occid: Unique numeric ID, or vector of IDs for occurrences
    :type occid: int
    :param siteid: Unique numeric ID, or vector of IDs for sites
    :type siteid: int
    :param format: Output format for publications. Default response is BibJSON, however many publications are not formatted properly for BibJSON, and so caution should be exercised. Response may be bibJSON or APA
    :type format: str

    :rtype: List[Publication]
    """
    return 'do some magic!'
