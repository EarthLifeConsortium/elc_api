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

from .elc import config, params, handlers, aux
from http_status import Status
from time import time
from flask import jsonify
import requests
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
    return_obj = list()
    desc_obj = dict()

    # Set runtime options

    try:
        options = params.set_options(req_args=connexion.request.args,
                                     endpoint='occ')

    except ValueError as err:
        return connexion.problem(status=err.args[0],
                                 title=Status(err.args[0]).name,
                                 detail=err.args[1],
                                 type='about:blank')

    # Cycle through external databases

    for db in config.db_list():

        t0 = time()

        # Configure parameter payload for api subquery

        try:
            payload = params.parse(db=db,
                                   req_args=connexion.request.args,
                                   endpoint='occ')

        except ValueError as err:
            return connexion.problem(status=err.args[0],
                                     title=Status(err.args[0]).name,
                                     detail=err.args[1],
                                     type='about:blank')

        # Database API call

        if db == 'neotoma':
            url_path = config.get('resource_api', db) + 'occurrence'
        if db == 'pbdb':
            url_path = config.get('resource_api', db) + 'occs/list.json'

        try:
            resp = requests.get(url_path,
                                params=payload,
                                timeout=config.get('default', 'timeout'))
            resp.raise_for_status()

        except requests.exceptions.HTTPError as err:
            return connexion.problem(status=resp.status_code,
                                     title=Status(resp.status_code).name,
                                     detail=str(err.args[0]),
                                     type='about:blank')

        except requests.exceptions.SSLError as err:
            return connexion.problem(status=495,
                                     title=Status(495).name,
                                     detail=str(err.args[0]),
                                     type='about:blank')

        except requests.exceptions.ConnectionError as err:
            return connexion.problem(status=502,
                                     title=Status(502).name,
                                     detail=str(err.args[0]),
                                     type='about:blank')

        except requests.exceptions.Timeout as err:
            return connexion.problem(status=504,
                                     title=Status(504).name,
                                     detail=str(err.args[0]),
                                     type='about:blank')

        except requests.exceptions.RequestException as err:
            return connexion.problem(status=500,
                                     title=Status(500).name,
                                     detail=str(err.args[0]),
                                     type='about:blank')

        # Check the Content-Type of the return and decode the JSON object

        if 'application/json' not in resp.headers.get('content-type'):
            msg = '{0:s} response is not of type application/json'.format(db)
            return connexion.problem(status=417,
                                     title=Status(417).name,
                                     detail=msg,
                                     type='about:blank')

        try:
            resp_json = resp.json()
        except ValueError as err:
            msg = '{0:s} JSON decode error: {1:s}'.format(db, err)
            return connexion.problem(status=500,
                                     title=Status(500).name,
                                     detail=msg,
                                     type='about:blank')

        # Build returned metadata object

        db_rec_name = config.get('db_rec_obj', db)
        desc_obj.update(license=config.get('default', 'license'),
                        retrieval_timestamp=aux.set_timestamp(),
                        link='http://earthlifeconsortium.org')
        db_meta = {db: {'subquery': resp.url,
                        'response_time': round(time()-t0, 3),
                        'record_count': len(resp_json.get(db_rec_name))}}
        desc_obj.update(db_meta)

        # Parse database response

        return_obj = handlers.occurrence(db=db,
                                         resp_json=resp_json,
                                         return_obj=return_obj)

    # Return composite data structure to client

    return jsonify(status='success', metadata=desc_obj, records=return_obj)
