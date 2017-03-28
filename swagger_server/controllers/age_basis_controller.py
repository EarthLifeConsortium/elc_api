import connexion
from swagger_server.models.agebasis import Agebasis
from swagger_server.models.error_model import ErrorModel
from datetime import date, datetime
from typing import List, Dict
from six import iteritems
from ..util import deserialize_date, deserialize_datetime


def age(occid=None, siteid=None):
    """
    Generation method of age estimates for the occurrence or site
    Samples often have assigned temporal uncertainty estimates, whether from C-14 dates, stratigraphic uncertainty, or other dating techniques.  This endpoint returns the basis for the age uncertainty estimate
    :param occid: Unique numeric ID, or vector of IDs for occurrences
    :type occid: int
    :param siteid: Unique numeric ID, or vector of IDs for sites
    :type siteid: int

    :rtype: List[Agebasis]
    """
    return 'do some magic!'
