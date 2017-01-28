"""RESTful API controller.

Endpoint for queries on geolocated sites.
"""

from flask import request, jsonify
import requests
import time


def site(occid = None, bbox = None, minage = None, maxage = None, agescale = None, timerule = None, taxon = None, includelower = None) -> str:
    """Return site identifiers from Neotoma and PBDB."""
    occ_return = list()
    desc_obj = dict()

    # Query the Neotoma Database (Occurrences)

    t0 = time.time()
    neotoma_base = 'http://apidev.neotomadb.org/v1/data/occurrences'
    payload = dict()

    if 'bbox' in request.args:
        payload.update(loc=request.args.get('bbox'))

    if 'minage' in request.args:
        payload.update(ageyoung=request.args.get('minage'))

    if 'maxage' in request.args:
        payload.update(ageold=request.args.get('maxage'))

    if 'agescale' in request.args:
        payload.update(XXX=request.args.get('agescale'))

    if 'timerule' in request.args:
        payload.update(XXX=request.args.get('timerule'))

    if 'includelower' in request.args:
        if request.args.get('includelower').lower() == 'false':
            payload.update(nametype='tax',
                           taxonname=request.args.get('taxon'))
        else:
            payload.update(nametype='base',
                           taxonname=request.args.get('taxon'))
    else:
        payload.update(nametype='base', taxonname=request.args.get('taxon'))

    if 'limit' in request.args:
        payload.update(limit=request.args.get('limit'))
    else:
        payload.update(limit='999999')

    if 'offset' in request.args:
        payload.update(XXX=request.args.get('offset'))

    neotoma_res = requests.get(neotoma_base, params=payload, timeout=None)

    if neotoma_res.status_code == 200:
        neotoma_json = neotoma_res.json()
        if 'data' in neotoma_json:
            for occ in neotoma_json['data']:
                db_occ_id = 'neot:occ:' + str(occ['OccurID'])
                occ_return.append({'occ_id': db_occ_id,
                                   'taxon': occ['TaxonName']})
            t1 = round(time.time() - t0, 5)
            desc_obj.update(neot_time=t1)
            desc_obj.update(neot_url=neotoma_res.url)
            desc_obj.update(neot_occs=len(neotoma_json['data']))
