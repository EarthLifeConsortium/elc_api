"""
RESTful API controller.

Endpoint for queries on taxonomic occurrences in time and space.
"""

# import connexion
# from swagger_server.models.error_model import ErrorModel
# from swagger_server.models.occurrence import Occurrence
# from datetime import date, datetime
# from typing import List, Dict
# from six import iteritems
# from ..util import deserialize_date, deserialize_datetime
from flask import request, jsonify
import requests
import time
from statistics import mean


def occ(bbox=None, minage=None, maxage=None, agescale=None, timerule=None,
        taxon=None, includelower=None, limit=None, offset=None, show=None):
    """
    Return occurrence identifiers from Neotoma and PBDB.

    With show=all, return expanded geography and age data for each occurrence.
    """
    # Initialization and parameter checks

    if request.args == {}:
        return jsonify(status_code=400, error='No parameters provided.')

    desc_obj = dict()
    occ_return = list()
    age_units = 'yr'
    geog_units = 'dec_deg_modern'
    full_return = False

    if show and show.lower() == 'all':
        full_return = True

    # Query the Neotoma Database (Occurrences)

    t0 = time.time()
    neotoma_base = 'http://apidev.neotomadb.org/v1/data/occurrences'
    payload = dict()
    age_scaler = 1

    if bbox:
        payload.update(bbox=bbox)

    if minage:
        payload.update(ageyoung=minage)

    if maxage:
        payload.update(ageold=maxage)

    if agescale and agescale.lower() == 'ma':
        age_scaler = 1e-06
        age_units = 'ma'
    elif agescale and agescale.lower() == 'ka':
        age_scaler = 1e-03
        age_units = 'ka'

    if timerule and timerule.lower() == 'major':
        payload.update(agedocontain=0)
    elif timerule and timerule.lower() == 'overlap':
        payload.update(agedocontain=1)

    if includelower and includelower.lower() == 'false':
        payload.update(nametype='tax', taxonname=taxon)
    else:
        payload.update(nametype='base', taxonname=taxon)

    if limit:
        payload.update(limit=limit)
    else:
        payload.update(limit='999999')

    if offset:
        payload.update(offset=offset)

    neotoma_res = requests.get(neotoma_base, params=payload, timeout=None)

    if neotoma_res.status_code == 200:
        neotoma_json = neotoma_res.json()
        if 'data' in neotoma_json:
            for occ in neotoma_json['data']:
                occ_obj = dict()
                occ_id = 'neot:occ:' + str(occ['OccurID'])
                occ_obj.update(occ_id=occ_id, taxon=occ['TaxonName'])

                if full_return:
                    taxon_id = 'neot:txn:' + str(occ['TaxonID'])
                    if occ['AgeOlder'] and occ['AgeYounger']:
                        max_age = float(occ['AgeOlder']) * age_scaler
                        min_age = float(occ['AgeYounger']) * age_scaler
                    else:
                        max_age = None
                        min_age = None
                    lat = mean([float(occ['LatitudeNorth']),
                                float(occ['LatitudeSouth'])])
                    lat = round(lat, 4)
                    lon = mean([float(occ['LongitudeEast']),
                                float(occ['LongitudeWest'])])
                    lon = round(lon, 4)
                    occ_obj.update(taxon_id=taxon_id, max_age=max_age,
                                   min_age=min_age, age_units=age_units,
                                   lat=lat, lon=lon, geog_units=geog_units)

                occ_return.append(occ_obj)

            t1 = round(time.time()-t0, 5)
            desc_obj.update(neot_time=t1)
            desc_obj.update(neot_url=neotoma_res.url)
            desc_obj.update(neot_occs=len(neotoma_json['data']))

    # Query the Paleobiology Database (Occurrences)

    t0 = time.time()
    pbdb_base = 'http://paleobiodb.org/data1.2/occs/list.json'
    payload = dict()
    age_scaler = 1e-06
    if full_return:
        payload.update(show='loc,coords,coll')
    payload.update(vocab='pbdb')

    if bbox:
        bbox_list = bbox.split(',')
        payload.update(lngmin=bbox_list[0], latmin=bbox_list[1],
                       lngmax=bbox_list[2], latmax=bbox_list[3])

    if minage:
        min_age_ma = int(minage) / 1000000
        payload.update(min_ma=str(min_age_ma))

    if maxage:
        max_age_ma = int(maxage) / 1000000
        payload.update(max_ma=str(max_age_ma))

    if agescale and agescale.lower() == 'ma':
        age_scaler = 1
        age_units = 'ma'
    elif agescale and agescale.lower() == 'ka':
        age_scaler = .001
        age_units = 'ka'

    if timerule:
        payload.update(timerule=timerule)

    if includelower and includelower.lower() == 'false':
        payload.update(taxon_name=taxon)
    else:
        payload.update(base_name=taxon)

    if limit:
        payload.update(limit=limit)
    else:
        payload.update(limit='999999')

    if offset:
        payload.update(offset=offset)

    pbdb_res = requests.get(pbdb_base, params=payload, timeout=None)

    if pbdb_res.status_code == 200:
        pbdb_json = pbdb_res.json()
        if 'records' in pbdb_json:
            for occ in pbdb_json['records']:
                occ_obj = dict()
                occ_id = 'pbdb:occ:' + str(occ['occurrence_no'])
                occ_obj.update(occ_id=occ_id, taxon=occ['accepted_name'])

                if full_return:
                    taxon_id = 'pbdb:txn:' + str(occ['accepted_no'])
                    if occ['max_ma'] and occ['min_ma']:
                        max_age = float(occ['max_ma']) * age_scaler
                        min_age = float(occ['min_ma']) * age_scaler
                    else:
                        max_age = None
                        min_age = None
                    lat = float(occ['lat'])
                    lat = round(lat, 4)
                    lon = float(occ['lng'])
                    lon = round(lon, 4)
                    occ_obj.update(taxon_id=taxon_id, max_age=max_age,
                                   min_age=min_age, age_units=age_units,
                                   lat=lat, lon=lon, geog_units=geog_units)

                occ_return.append(occ_obj)

            t1 = round(time.time()-t0, 5)
            desc_obj.update(pbdb_time=t1)
            desc_obj.update(pbdb_url=pbdb_res.url)
            desc_obj.update(pbdb_occs=len(pbdb_json['records']))

    # Composite response

    return jsonify(description=desc_obj, data=occ_return)
