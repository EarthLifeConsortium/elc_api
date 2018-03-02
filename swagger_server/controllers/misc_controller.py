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
from ..elc import params, aux, ages, geog
from http_status import Status
from time import time
from flask import jsonify


def paleocoords(coords=None, age=None, ageunits=None):
    """
    Return paleocoordinates for a given age and modern lat/lon.

    :param geog: Comma separated latitude,longitude
    :type geog: str (decimal degrees -180 to 180)
    :param age: Numerical or geologic age
    :param age: str
    :param ageunits: Units of measure for the ages specified (and returned)
    :type ageunits: str ('yr', 'ka' or 'ma')

    """
    t0 = time()
    desc_obj = dict()
    ext_provider = 'EarthByte GPlates (Wright et al. 2013) via Macrostrat'

    # Set runtime options

    try:
        options = params.set_options(req_args=connexion.request.args,
                                     endpoint='misc')

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
                     endpoint='paleocoords')

    except ValueError as err:
        return connexion.problem(status=err.args[0],
                                 title=Status(err.args[0]).name,
                                 detail=err.args[1],
                                 type='about:blank')

    # Determine paleocoordinates and resolve geologic age if necessary

    try:
        paleo_lon, paleo_lat = geog.get_geog(coords=coords,
                                             age=age,
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
                                       sub_tag='paleo_coord'))

    # Return data structure to client

    return_obj = {'paleo_lat': paleo_lat,
                  'paleo_lon': paleo_lon}

    return jsonify(metadata=desc_obj, records=return_obj)


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
    ext_provider = 'International Commission on Stratigraphy (2013) via PBDB'

    # Set runtime options

    try:
        options = params.set_options(req_args=connexion.request.args,
                                     endpoint='misc')

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

    # Determine time bounds and resolve geologic age if necessary

    try:
        early_age, late_age = ages.get_age(age_range=agerange,
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
