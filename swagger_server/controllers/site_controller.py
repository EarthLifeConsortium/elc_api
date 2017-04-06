"""
RESTful API controller.

Endpoint for queries on geolocated sites.
"""

# import connexion
# from swagger_server.models.error_model import ErrorModel
# from swagger_server.models.site import Site
# from datetime import date, datetime
# from typing import List, Dict
# from six import iteritems
# from ..util import deserialize_date, deserialize_datetime
from flask import request, jsonify
import requests
import time
from statistics import mean


def site(occid=None, bbox=None, minage=None, maxage=None, agescale=None, timerule=None, taxon=None, includelower=None):
    """
    Return site identifiers from Neotoma and PBDB.
    """
    # Initialization and parameter checks

    if request.args == {}:
        return jsonify(status_code=400, error='No parameters provided.')

    desc_obj = dict()
    occ_return = list()
    age_units = 'ma'
    geog_units = 'dec_deg_modern'
    full_return = False

    if show and show.lower() == 'all':
        full_return = True

    # Query the Neotoma Database (Sites)

    t0 = time.time()
    neotoma_base = 'http://apidev.neotomadb.org/v1/data/datasets'
    payload = dict()

    if bbox:
        payload.update(bbox=bbox)

    if agescale and agescale.lower() == 'yr':
        age_scaler = 1
        age_units = 'yr'
        if minage:
            payload.update(ageyoung=int(minage))
        if maxage:
            payload.update(ageold=int(maxage))
    elif agescale and agescale.lower() == 'ka':
        age_scaler = 1e-03
        age_units = 'ka'
        if minage:
            payload.update(ageyoung=int(minage/age_scaler))
        if maxage:
            payload.update(ageold=int(maxage/age_scaler))
    else:
        age_scaler = 1e-06
        age_units = 'ma'
        if minage:
            payload.update(ageyoung=int(minage/age_scaler))
        if maxage:
            payload.update(ageold=int(maxage/age_scaler))

    if timerule and timerule.lower() == 'major':
        payload.update(agedocontain=0)
    elif timerule and timerule.lower() == 'overlap':
        payload.update(agedocontain=1)

    if includelower and includelower.lower() == 'false':
        payload.update(nametype='tax', taxonname=taxon)
    else:
        payload.update(nametype='base', taxonname=taxon)

    neotoma_res = requests.get(neotoma_base, params=payload, timeout=None)

    # Composite response

    return jsonify(description=desc_obj, data=occ_return)
