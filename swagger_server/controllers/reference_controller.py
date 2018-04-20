"""
RESTful API controller.

Endpoint for queries on references (publications) used as primary
citations in the subordinate databases.
"""

#  from swagger_server.models.error_model import ErrorModel
#  from swagger_server.models.reference import Occurrence
#  from datetime import date, datetime
#  from typing import List, Dict
#  from six import iteritems
#  from ..util import deserialize_date, deserialize_datetime

import connexion
from ..elc import config, params, aux, subreq
from ..handlers import router
from http_status import Status
from time import time
from flask import jsonify


def ref(idnumbers=None, show=None, output=None):
    """
    Literature references/publications.

    Accepts the following dataset types: occ, col, dst, ref

    :param idnumbers: List of formatted ids [dbname]:[datasettype]:[number]
    :type idnumbers: str
    :param show: Return identifiers or stats (defult=full, idx, poll)
    :type show: str
    :param output: Response format (defult=bibjson, csv)
    :type output: str

    """
    return_obj = list()
    desc_obj = dict()

    # Set runtime options

    try:
        options = params.set_options(req_args=connexion.request.args,
                                     endpoint='ref')

    except ValueError as err:
        return connexion.problem(status=err.args[0],
                                 title=Status(err.args[0]).name,
                                 detail=err.args[1],
                                 type='about:blank')

    # Cycle through external databases

    for db in config.db_list():

        # temporary (hopefully) shim
        if db == 'neotoma':
            continue

        t0 = time()

        # Configure parameter payload for api subquery

        try:
            payload = params.parse(req_args=connexion.request.args,
                                   options=options,
                                   db=db,
                                   endpoint='ref')

        except ValueError as err:
            return connexion.problem(status=err.args[0],
                                     title=Status(err.args[0]).name,
                                     detail=err.args[1],
                                     type='about:blank')

        # Database API call

        url_path = ''.join([config.get('resource_api', db),
                            config.get('db_ref_endpt', db)])

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
                                            endpoint='ref')

        # Build returned metadata object

        desc_obj.update(aux.build_meta(options))

        desc_obj.update(aux.build_meta_sub(data=return_obj,
                                           source=api_call,
                                           t0=t0,
                                           sub_tag=db,
                                           options=options))

    # Return composite data structure to client

    if options.get('show') == 'poll':
        return jsonify(desc_obj)
    if options.get('show') == 'idx':
        return jsonify(aux.get_id_numbers(data=return_obj, endpoint='ref'))
    else:
        return jsonify(metadata=desc_obj, records=return_obj)
