"""RESTful API controller.

Endpoint for queries on taxonomic occurrences in time and space.
"""

from flask import request, jsonify
import requests
import time


def occ(bbox=None, minage=None, maxage=None, agescale=None, timerule=None,
        taxon=None, includelower=None, limit=None, offset=None) -> str:
    """Return occurrence identifiers from Neotoma and PBDB."""
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

    # Query the Paleobiology Database (Occurrences)

    t0 = time.time()
    pbdb_base = 'http://paleobiodb.org/data1.2/occs/list.json'
    payload = dict()
    # payload.update(show='loc,coords,coll')
    payload.update(vocab='pbdb')

    if 'bbox' in request.args:
        payload.update(XXX=request.args.get('bbox'))

    if 'minage' in request.args:
        payload.update(minage=request.args.get('minage'))

    if 'maxage' in request.args:
        payload.update(maxage=request.args.get('maxage'))

    if 'agescale' in request.args:
        payload.update(XXX=request.args.get('agescale'))

    if 'timerule' in request.args:
        payload.update(timerule=request.args.get('timerule'))

    if 'includelower' in request.args:
        if request.args.get('includelower').lower() == 'false':
            payload.update(taxon_name=request.args.get('taxon'))
        else:
            payload.update(base_name=request.args.get('taxon'))
    else:
        payload.update(base_name=request.args.get('taxon'))

    if 'limit' in request.args:
        payload.update(limit=request.args.get('limit'))
    else:
        payload.update(limit='999999')

    if 'offset' in request.args:
        payload.update(XXX=request.args.get('offset'))

    pbdb_res = requests.get(pbdb_base, params=payload, timeout=None)

    if pbdb_res.status_code == 200:
        pbdb_json = pbdb_res.json()
        if 'records' in pbdb_json:
        for occ in pbdb_json['records']:
            db_occ_id = 'pbdb:occ:' + str(occ['occurrence_no'])
            occ_return.append({'occ_id': db_occ_id,
                               'taxon': occ['identified_name']})
            t1 = round(time.time() - t0, 5)
            desc_obj.update(pbdb_time=t1)
            desc_obj.update(pbdb_url=pbdb_res.url)
            desc_obj.update(pbdb_occs=len(pbdb_json['records']))

    # Composite response 

    return jsonify(description=desc_obj, data=occ_return)
