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
from ..elc import config, params, aux
from ..handlers import router
from http_status import Status
from time import time
from flask import jsonify
import requests


def loc(idlist=None, bbox=None, agerange=None, ageunits=None, timerule=None,
        show=None, output=None):
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
                                        endpoint='loc')

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
        return jsonify(aux.get_id_numbers(data=return_obj, endpoint='locale'))
    else:
        return jsonify(metadata=desc_obj, records=return_obj)
