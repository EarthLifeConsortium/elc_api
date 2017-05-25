"""
RESTful API controller.

Endpoint for queries on taxonomic occurrences in time and space.
"""

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
    age_units = 'ma'
    geog_units = 'dec_deg_modern'
    full_return = False

    if show and show.lower() == 'all':
        full_return = True

    # Query the Neotoma Database (Occurrences)

    t0 = time.time()
    base_url = 'http://apidev.neotomadb.org/v1/data/occurrences'
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

    if limit:
        payload.update(limit=limit)
    else:
        payload.update(limit='999999')

    if offset:
        payload.update(offset=offset)

    resp = requests.get(base_url, params=payload, timeout=None)

    if resp.status_code == 200:
        resp_json = resp.json()
        if 'data' in resp_json:
            for occ in resp_json['data']:
                occ_obj = dict()
                occ_id = 'neot:occ:' + str(occ['OccurID'])
                occ_obj.update(occ_id=occ_id, taxon=occ['TaxonName'])

                if full_return:
                    taxon_id = 'neot:txn:' + str(occ['TaxonID'])
                    if occ['AgeOlder'] and occ['AgeYounger']:
                        max_age = occ['AgeOlder'] * age_scaler
                        min_age = occ['AgeYounger'] * age_scaler
                    else:
                        max_age = None
                        min_age = None
                    lat = mean([occ['LatitudeNorth'],
                                occ['LatitudeSouth']])
                    # lat = round(lat, 4)
                    lon = mean([occ['LongitudeEast'],
                                occ['LongitudeWest']])
                    # lon = round(lon, 4)
                    occ_obj.update(taxon_id=taxon_id, max_age=max_age,
                                   min_age=min_age, age_units=age_units,
                                   lat=lat, lon=lon, geog_units=geog_units)

                occ_return.append(occ_obj)

            t1 = round(time.time()-t0, 3)
            desc_obj.update(neotoma={'response_time': t1,
                                     'subqueries': resp.url,
                                     'record_count': len(resp_json['data'])})

    # Query the Paleobiology Database (Occurrences)

    t0 = time.time()
    base_url = 'http://paleobiodb.org/data1.2/occs/list.json'
    payload = dict()
    if full_return:
        payload.update(show='loc,coords,coll')
    payload.update(vocab='pbdb')

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

    if limit:
        payload.update(limit=limit)
    else:
        payload.update(limit='999999')

    if offset:
        payload.update(offset=offset)

    resp = requests.get(base_url, params=payload, timeout=None)

    if resp.status_code == 200:
        resp_json = resp.json()
        if 'records' in resp_json:
            for occ in resp_json['records']:
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

            t1 = round(time.time()-t0, 3)
            desc_obj.update(pbdb={'response_time': t1,
                                  'subqueries': resp.url,
                                  'record_count': len(resp_json['records'])})

    # Composite response

    return jsonify(description=desc_obj, records=occ_return)
