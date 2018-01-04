"""
RESTful API controller.

Endpoint for queries on taxonomic occurrences in time and space.
"""

import connexion
#  from swagger_server.models.error_model import ErrorModel
#  from swagger_server.models.occurrence import Occurrence
#  from datetime import date, datetime
#  from typing import List, Dict
#  from six import iteritems
#  from ..util import deserialize_date, deserialize_datetime

from .elc import config, params
from http_status import Status
import pdb


def occ(bbox=None, minage=None, maxage=None, agescale=None,
        timerule=None, taxon=None, includelower=None, limit=None,
        offset=None, show=None, output=None):
    """
    Fossil occurrences in a specific place and time.

    :param bbox: [lonW, latS, lonE, latN] or GeoJSON
    :type bbox: str
    :param minage: Default units as Ma, overridden by agescale
    :type minage: float
    :param maxage: Default units as Ma, overridden by agescale
    :type maxage: float
    :param agescale: Maxage and minage units (def=ma, ka, yr)
    :type agescale: str
    :param timerule: Temporal bound (def=contain, major, overlap)
    :type timerule: str
    :param taxon: Taxonomic name, ASCII encode
    :type taxon: str
    :param includelower: Include sub-taxa (def=True)
    :type includelower: bool
    :param limit: Limit the number of records in the response
    :type limit: int
    :param offset: Begin the response from a designated point
    :type offset: int
    :param show: Return identifiers or stats (def=full, idx, poll)
    :type show: str
    :param output: Response format (def=json, csv)
    :type output: str

    :rtype: List[Occurrence]
    """
    for db in config.db_list():

        # Configure parameter payload for api subquery

        try:
            payload = params.parse(req_args=connexion.request.args,
                                   db=db,
                                   endpoint='occ')

        except ValueError as err:
            return connexion.problem(status=err.args[0],
                                     title=Status(err.args[0]).name,
                                     detail=err.args[1],
                                     type='about:blank')

    return payload
