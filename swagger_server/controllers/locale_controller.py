"""
RESTful API controller.

Endpoint for queries on data locales (collections and datasets).
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


def loc(idlist=None, bbox=None, agerange=None, ageunits=None, timerule=None,
        paleocoords=None, limit=None, offset=None, show=None, output=None):
    """
    Return locale identifiers from Neotoma and PBDB.

    A locale in PBDB is a collection, in Neotoma it is every individual
    dataset in a site.

    :param idlist: Comma separated list of col or dst ids as db:dtype:number
    :type idlist: str
    :param bbox: [lonW, latS, lonE, latN] or GeoJSON
    :type bbox: str
    :param agerange: Comma separated numerical or textual geologic ages
    :type agerange: str
    :param ageunits: Maxage and minage units (default=ma, ka, yr)
    :type ageunits: str
    :param timerule: Temporal bound (default=contain, major, overlap)
    :type timerule: str
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
                                     endpoint='loc')

    except ValueError as err:
        return connexion.problem(status=err.args[0],
                                 title=Status(err.args[0]).name,
                                 detail=err.args[1],
                                 type='about:blank')

    # Cycle through external databases

    for db in config.db_list():

        t0 = time()
        options.update(run=True)

        # Configure parameter payload for api subquery

        try:
            payload = params.parse(req_args=connexion.request.args,
                                   options=options,
                                   db=db,
                                   endpoint='loc')

        except ValueError as err:
            return connexion.problem(status=err.args[0],
                                     title=Status(err.args[0]).name,
                                     detail=err.args[1],
                                     type='about:blank')

        # skip this database if no ids specified (run option is False)

        if not options.get('run'):
            continue

        # Database API call

        url_path = ''.join([config.get('resource_api', db),
                            config.get('db_loc_endpt', db)])

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
                                            endpoint='loc')

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
            return jsonify(aux.get_id_numbers(data=return_obj,
                                              endpoint='loc'))
        else:
            return jsonify(metadata=desc_obj, records=return_obj)

    #  elif options.get('
    elif options.get('output') == 'csv':
        if return_obj:
            filename = aux.build_filename(endpoint='loc', data=return_obj)
            return flask_csv.send_csv(return_obj,
                                      filename,
                                      return_obj[0].keys())
        else:
            msg = 'Unable to generate CSV file. Search returned no records.'
            return jsonify(status=204,
                           title=Status(204).name,
                           detail=msg,
                           type='about:blank')
