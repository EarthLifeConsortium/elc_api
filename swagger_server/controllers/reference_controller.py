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
from ..elc import config, params, aux, subreq, formatter
from ..handlers import router
from http_status import Status
from time import time
from flask import jsonify, Response


def ref(idlist=None, show=None, output=None, run=None):
    """Bibliographic references, publications and other sources."""
    return_obj = list()
    desc_obj = dict()

    # Log this request
    
    print(datetime.datetime.now(), " [", str(os.getpid()), "]")
    print("Request: " + connexion.request.method + " " + connexion.request.base_url,
          connexion.request.args.to_dict() )
    
    # Set runtime options

    try:
        options = params.set_options(req_args=connexion.request.args,
                                     endpoint='ref')

    except ValueError as err:
        return connexion.problem(status=err.args[0],
                                 title=Status(err.args[0]).name,
                                 detail=err.args[1],
                                 type='about:blank')

    run_list = aux.get_run_list(connexion.request.args.get('run'))

    # Cycle through external databases

    for db in run_list:

        t0 = time()
        options.update(skip=False)

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

        # skip this database if no ids specified

        if options.get('skip'):
            continue

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

    # Log that the request is complete
    
    print("Request complete.")
    
    # Return composite data structure to client

    if options.get('output') in ['json', 'bibjson']:
        if options.get('show') == 'poll':
            return jsonify(desc_obj)
        if options.get('show') == 'idx':
            return jsonify(aux.get_id_numbers(data=return_obj,
                                              endpoint='ref'))
        else:
            if options.get('output') == 'bibjson':
                return jsonify(metadata=desc_obj,
                               records=formatter.type_bibjson(return_obj))
            else:
                return jsonify(metadata=desc_obj, records=return_obj)

    elif options.get('output') == 'json':
        if options.get('show') == 'poll':
            return jsonify(desc_obj)
        if options.get('show') == 'idx':
            return jsonify(aux.get_id_numbers(data=return_obj,
                                              endpoint='ref'))
        else:
            return jsonify(metadata=desc_obj, records=return_obj)

    elif options.get('output') == 'csv':
        if return_obj:
            tab_data = formatter.type_csv(return_obj)
            return Response((x for x in tab_data), mimetype='text/csv')
        else:
            msg = 'Unable to generate CSV file. Search returned no records.'
            return jsonify(status=204,
                           title=Status(204).name,
                           detail=msg,
                           type='about:blank')

    elif options.get('output') == 'file':
        import flask_csv
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

    elif options.get('output') == 'ris':
        if return_obj:
            ris = formatter.type_ris(return_obj)
            return Response((x for x in ris), mimetype='text/plain')
        else:
            msg = 'Unable to generate RIS file. Search returned no records.'
            return jsonify(status=204,
                           title=Status(204).name,
                           detail=msg,
                           type='about:blank')
