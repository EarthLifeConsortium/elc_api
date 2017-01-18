'''
RESTful API primary controller.
Dispatch layer uses the OpenAPI Connexion library (https://connexion.readthedocs.io).

author: jpjenk@icloud.com
data:   Jan. 2017

'''
# Flask web microframework (http://flask.pocoo.org)
from flask import request, jsonify, json, Response

# Requests HTTP library (http://docs.python-requests.org)
import requests

import time

#
# Return the Age Calculation Basis
#
def age(occid = None, siteid = None) -> str:
    return 'age basis endpoint'

#
# Return Data as Gridded Assemblages
#
def grid(agebound = None, agebin = None, ageunit = None, bbox = None, spatialbin = None, varunit = None, presence = None) -> str:
    return 'gridded assemblage endpoint'

#
# Return Occurrence Data
#
def occ(bbox = None, minage = None, maxage = None, agescale = None, timerule = None, taxon = None, includelower = None, limit = None, offset = None) -> str: 
    t0 = time.time()
    occ_return = list()
    desc_obj = dict()

    #
    # Query the Neotoma Database (Occurrences)
    #
    neotoma_base = 'http://apidev.neotomadb.org/v1/data/occurrences'
    payload=dict()

    if 'bbox' in request.args:
        payload.update(loc=request.args.get('bbox'))

    if 'minAge' in request.args:
        payload.update(ageyoung=request.args.get('minAge'))

    if 'maxAge' in request.args:
        payload.update(ageold=request.args.get('maxAge'))

    if 'ageScale' in request.args:
        payload.update(XXX=request.args.get('ageScale'))

    if 'timeRule' in request.args:
        payload.update(XXX=request.args.get('timeRule'))

    if 'include_lower' in request.args:
        if request.args.get('include_lower').lower() == 'true':
            payload.update(nametype='base', taxonname=request.args.get('taxon'))
        else:
            payload.update(nametype='tax', taxonname=request.args.get('taxon'))
    else:
        payload.update(nametype='tax', taxonname=request.args.get('taxon'))

    if 'limit' in request.args:
        payload.update(limit=request.args.get('limit'))
    else:
        payload.update(limit='999999')

    if 'offset' in request.args:
        payload.update(XXX=request.args.get('offset'))

    neotoma_res = requests.get(neotoma_base, params=payload, timeout=None)

    if neotoma_res.status_code == 200:
        occ_cnt = 0
        neotoma_json = neotoma_res.json()
        for occ in neotoma_json['data']:
            occ_cnt += 1
            db_occ_id = 'neot:occ:' + str(occ['OccurID'])
            occ_return.append({'occ_id': db_occ_id, 'taxon': occ['TaxonName']})
        desc_obj.update(neotoma_url=neotoma_res.url)
        desc_obj.update(neot_occs = occ_cnt)

    #
    # Query the Paleobiology Database (Occurrences)
    #
    pbdb_base = 'http://paleobiodb.org/data1.2/occs/list.json'
    payload=dict()
    payload.update(show='loc,coords,coll')
    payload.update(vocab='pbdb')

    if 'bbox' in request.args:
        payload.update(XXX=request.args.get('bbox'))

    if 'minAge' in request.args:
        payload.update(minage=request.args.get('minAge'))

    if 'maxAge' in request.args:
        payload.update(maxage=request.args.get('maxAge'))

    if 'ageScale' in request.args:
        payload.update(XXX=request.args.get('ageScale'))

    if 'timeRule' in request.args:
        payload.update(timerule=request.args.get('timeRule'))

    if 'include_lower' in request.args:
        if request.args.get('include_lower').lower() == 'true':
            payload.update(base_name=request.args.get('taxon'))
        else:
            payload.update(taxon_name=request.args.get('taxon'))
    else:
        payload.update(taxon_name=request.args.get('taxon'))

    if 'limit' in request.args:
        payload.update(limit=request.args.get('limit'))
    else:
        payload.update(limit='999999')

    if 'offset' in request.args:
        payload.update(XXX=request.args.get('offset'))

    pbdb_res = requests.get(pbdb_base, params=payload, timeout=None)

    if pbdb_res.status_code == 200:
        occ_cnt = 0
        pbdb_json = pbdb_res.json()
        for occ in pbdb_json['records']:
            occ_cnt += 1
            db_occ_id = 'pbdb:occ:' + str(occ['occurrence_no'])
            occ_return.append({'occ_id': db_occ_id, 'taxon': occ['identified_name']})
        t1 = round(time.time() - t0, 5)
        desc_obj.update(time = t1)
        desc_obj.update(pbdb_url = pbdb_res.url)
        desc_obj.update(pbdb_occs = occ_cnt)
        return jsonify(description = desc_obj, data = occ_return)
    else:
        return 'Error code ' + str(pbdb_res.status_code) 
#
# Return Publication Data
#
def pub(occid = None, siteid = None, format = None) -> str:
    return 'publications endpoint'

#
# Return Site Data
#
def site(occid = None, bbox = None, minage = None, maxage = None, agescale = None, timerule = None, taxon = None, includelower = None) -> str:
    return 'site endpoint'

#
# Return Taxonomic Data
#
def taxon(taxon = None, includelower = None, hierarchy = None) -> str:
    t0 = time.time()
    occ_return = list()
    desc_obj = dict()

    #
    # Query the Neotoma Database (Taxonomy)
    #
    neotoma_base = 'http://apidev.neotomadb.org/v1/data/taxa'
    payload=dict()





    return 'taxonomy endpoint'
