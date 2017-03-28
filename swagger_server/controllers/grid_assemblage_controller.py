import connexion
from swagger_server.models.assemblage import Assemblage
from swagger_server.models.error_model import ErrorModel
from datetime import date, datetime
from typing import List, Dict
from six import iteritems
from ..util import deserialize_date, deserialize_datetime


def grid(agebound=None, agebin=None, ageunit=None, bbox=None, spatialbin=None, varunit=None, presence=None):
    """
    Gridded assemblage data
    Returns assemblage data at pre-built grid sizes for faster returns
    :param agebound: netsi
    :type agebound: str
    :param agebin: netsi
    :type agebin: str
    :param ageunit: netsi
    :type ageunit: str
    :param bbox: netsi
    :type bbox: str
    :param spatialbin: netsi
    :type spatialbin: str
    :param varunit: netsi
    :type varunit: str
    :param presence: netsi
    :type presence: bool

    :rtype: List[Assemblage]
    """
    return 'do some magic!'
