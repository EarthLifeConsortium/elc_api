"""
REST dispatcher.

Endpoint for miscelaneous ELC public functions:

/misc/timebound    - resolve min and max time bounds for specified geo ages

"""
#  from swagger_server.models.assemblage import Timebound
#  from swagger_server.models.error_model import ErrorModel
#  from datetime import date, datetime
#  from typing import List, Dict
#  from six import iteritems
#  from ..util import deserialize_date, deserialize_datetime
import connexion
from ..elc import params, aux
from http_status import Status
from time import time
from flask import jsonify


def timebound(agerange=None, ageunits=None):
    """
    Return min and max ages given a specified bound and units.

    :param agerange: Comma separated numerical or textual geologic ages
    :type agerange: str
    :param ageunits: Units of measure for the ages specified (and returned)
    :type ageunits: str ('yr', 'ka' or 'ma')

    """
    t0 = time()
    desc_obj = dict()
    ext_provider = 'International Commission on Stratigraphy (2013-01)'

    # Set runtime options

    try:
        options = params.set_options(req_args=connexion.request.args,
                                     endpoint='occ')

    except ValueError as err:
        return connexion.problem(status=err.args[0],
                                 title=Status(err.args[0]).name,
                                 detail=err.args[1],
                                 type='about:blank')

    # Call parse function to check for parameter errors

    try:
        params.parse(req_args=connexion.request.args,
                     options=options,
                     db='pbdb',
                     endpoint='timebound')

    except ValueError as err:
        return connexion.problem(status=err.args[0],
                                 title=Status(err.args[0]).name,
                                 detail=err.args[1],
                                 type='about:blank')

    # Determin time bounds and resolve geologic age if necessary

    try:
        early_age, late_age = aux.set_age(age_range=agerange,
                                          options=options)

    except ValueError as err:
        return connexion.problem(status=err.args[0],
                                 title=Status(err.args[0]).name,
                                 detail=err.args[1],
                                 type='about:blank')

    # Build returned metadata object

    desc_obj.update(aux.build_meta(ageunits=options.get('ageunits')))

    desc_obj.update(aux.build_meta_sub(source=ext_provider,
                                       t0=t0,
                                       sub_tag='geo_age'))

    # Return data structure to client

    return_obj = {'early_age': early_age,
                  'late_age': late_age}

    return jsonify(metadata=desc_obj, records=return_obj)
