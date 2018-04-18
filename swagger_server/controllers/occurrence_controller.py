"""
RESTful API controller.

Endpoint for queries on taxonomic occurrences in time and space.
"""

#  from swagger_server.models.error_model import ErrorModel
#  from swagger_server.models.occurrence import Occurrence
#  from datetime import date, datetime
#  from typing import List, Dict
#  from six import iteritems
#  from ..util import deserialize_date, deserialize_datetime

import connexion
from ..elc import config, params, aux
from ..handlers import router
from http_status import Status
from time import time
from flask import jsonify
import requests


def occ(bbox=None, agerange=None, ageuits=None, timerule=None, taxon=None,
        includelower=None, paleocoords=None, limit=None, offset=None,
        show=None, output=None):
    """
    Fossil occurrences in a specific place and time.

    :param bbox: [lonW, latS, lonE, latN] or GeoJSON
    :type bbox: str
    :param agerange: Comma separated numerical or textual geologic ages
    :type agerange: str
    :param ageunits: Maxage and minage units (default=ma, ka, yr)
    :type ageunits: str
    :param timerule: Temporal bound (default=contain, major, overlap)
    :type timerule: str
    :param taxon: Taxonomic name, ASCII encode
    :type taxon: str
    :param includelower: Include sub-taxa (defult=True)
    :type includelower: bool
    :param limit: Limit the number of records in the response
    :type limit: int
    :param offset: Begin the response from a designated point
    :type offset: int
    :param show: Return identifiers or stats (defult=full, idx, poll)
    :type show: str
    :param output: Response format (defult=json, csv)
    :type output: str

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
            payload = params.parse(req_args=connexion.request.args,
                                   options=options,
                                   db=db,
                                   endpoint='occ')

        except ValueError as err:
            return connexion.problem(status=err.args[0],
                                     title=Status(err.args[0]).name,
                                     detail=err.args[1],
                                     type='about:blank')

        # Database API call

        url_path = ''.join([config.get('resource_api', db),
                            config.get('db_occ_endpt', db)])
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

        # Parse database response

        return_obj = router.decode_occs(resp_json=resp_json,
                                        return_obj=return_obj,
                                        options=options,
                                        db=db,
                                        endpoint='occ')

        # Build returned metadata object

        desc_obj.update(aux.build_meta(ageunits=options.get('ageunits'),
                                       coords=options.get('coords')))

        desc_obj.update(aux.build_meta_sub(data=return_obj,
                                           source=resp.url,
                                           t0=t0,
                                           sub_tag=db,
                                           options=options))

    # Return composite data structure to client

    if options.get('show') == 'poll':
        return jsonify(desc_obj)
    if options.get('show') == 'idx':
        return jsonify(aux.get_id_numbers(data=return_obj, endpoint='occ'))
    else:
        return jsonify(metadata=desc_obj, records=return_obj)
