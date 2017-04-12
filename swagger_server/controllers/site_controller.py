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

    For this API, a site is considered to be a geolocated group of 
    Neotoma datasets and PBDB collections.
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

    # t0 = time.time()
    # neotoma_base = 'http://apidev.neotomadb.org/v1/data/datasets'
    # payload = dict()

    # ### if occid:

    # if bbox:
    #     payload.update(bbox=bbox)

    # if agescale and agescale.lower() == 'yr':
    #     age_scaler = 1
    #     age_units = 'yr'
    #     if minage:
    #         payload.update(ageyoung=int(minage))
    #     if maxage:
    #         payload.update(ageold=int(maxage))
    # elif agescale and agescale.lower() == 'ka':
    #     age_scaler = 1e-03
    #     age_units = 'ka'
    #     if minage:
    #         payload.update(ageyoung=int(minage/age_scaler))
    #     if maxage:
    #         payload.update(ageold=int(maxage/age_scaler))
    # else:
    #     age_scaler = 1e-06
    #     age_units = 'ma'
    #     if minage:
    #         payload.update(ageyoung=int(minage/age_scaler))
    #     if maxage:
    #         payload.update(ageold=int(maxage/age_scaler))

    # if timerule and timerule.lower() == 'major':
    #     payload.update(agedocontain=0)
    # elif timerule and timerule.lower() == 'overlap':
    #     payload.update(agedocontain=1)

    # if includelower and includelower.lower() == 'false':
    #     payload.update(nametype='tax', taxonname=taxon)
    # else:
    #     payload.update(nametype='base', taxonname=taxon)

    # neotoma_res = requests.get(neotoma_base, params=payload, timeout=None)
    
    # ### Parse neotoma response

    # Query the Paleobiology Database (Sites)

    t0 = time.time()
    pbdb_base = 'http://paleobiodb.org/data1.2/colls/list.json'
    payload = dict()
    payload.update(show='loc,coords,coll')
    payload.update(vocab='pbdb')

    if occid:
        payload.update(occ_id=occid)

    if bbox:
        bbox_list = bbox.split(',')
        payload.update(lngmin=bbox_list[0], latmin=bbox_list[1],
                       lngmax=bbox_list[2], latmax=bbox_list[3])

    if agescale and agescale.lower() == 'yr':
        age_scaler = 1e06
        age_units = 'yr'
        if minage:
            payload.update(min_ma=float(minage)/age_scaler)
        if maxage:
            payload.update(max_ma=float(maxage)/age_scaler)
    elif agescale and agescale.lower() == 'ka':
        age_scaler = 1e03
        age_units = 'ka'
        if minage:
            payload.update(min_ma=float(minage)/age_scaler)
        if maxage:
            payload.update(max_ma=float(maxage)/age_scaler)
    else:
        age_scaler = 1
        age_units = 'ma'
        if minage:
            payload.update(min_ma=minage)
        if maxage:
            payload.update(max_ma=maxage)

    if timerule:
        payload.update(timerule=timerule)

    if includelower and includelower.lower() == 'false':
        payload.update(taxon_name=taxon)
    else:
        payload.update(base_name=taxon)

    pbdb_res = requests.get(pbdb_base, params=payload, timeout=None)

    if pbdb_res.status_code == 200:
        pbdb_json = pbdb_res.json()
        if 'records' in pbdb_json:
            for site in pbdb_json['records']:
                site_obj = dict()
                site_id = 'pbdb:sit:' + str(site['collection_no'])
                site_obj.update(site_id=site_id,
                                site_name=site['collection_name'],
                                lat=site['lat'],
                                lon=site['lng'])

            t1 = round(time.time()-t0, 5)
            desc_obj.update(pbdb_time=t1)
            desc_obj.update(pbdb_url=pbdb_res.url)
            desc_obj.update(pbdb_occs=len(pbdb_json['records']))

    # Composite response

    return jsonify(description=desc_obj, records=occ_return)
