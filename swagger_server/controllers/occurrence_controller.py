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
import flask_csv
from ..elc import config, params, aux, subreq
from ..handlers import router
from http_status import Status
from time import time
from flask import jsonify


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
            resp_json, api_call = subreq.trigger(url_path, payload, db)

        except ValueError as err:
            return connexion.problem(status=err.args[0],
                                     title=Status(err.args[0]).name,
                                     detail=err.args[1],
                                     type='about:blank')

        # Parse database response

        return_obj = router.response_decode(resp_json=resp_json,
                                            return_obj=return_obj,
                                            options=options,
                                            db=db,
                                            endpoint='occ')

        # Build returned metadata object

        desc_obj.update(aux.build_meta(options))

        desc_obj.update(aux.build_meta_sub(data=return_obj,
                                           source=api_call,
                                           t0=t0,
                                           sub_tag=db,
                                           options=options))

    # Return composite data structure to client

    if options.get('output') == 'json':
        if options.get('show') == 'poll':
            return jsonify(desc_obj)
        if options.get('show') == 'idx':
            return jsonify(aux.get_id_numbers(data=return_obj, endpoint='occ'))
        else:
            return jsonify(metadata=desc_obj, records=return_obj)
    elif options.get('output') == 'csv':
        filename = aux.build_filename(endpoint='occ', data=return_obj)
        return flask_csv.send_csv(return_obj, filename, return_obj[0].keys())
