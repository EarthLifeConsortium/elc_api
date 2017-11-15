"""
RESTful API controller.

Endpoint for miscelaneous queries on specific species taxonomy.
"""

import requests
import time
import connexion
import json
from collections import OrderedDict
from flask import request, jsonify, Response
from .ControllerCommon import params, settings, formatters

import pdb

def tax(taxon=None, includelower=None, hierarchy=None):
    """
    Return taxonomic hierarchy and subtaxa in various formats.

    :arg format: json, itis or csv formatted return
    """
    # Parameter checks
    if not bool(request.args):
        return connexion.problem(status=400,
                                 title='Bad Request',
                                 detail='No parameters provided.',
                                 type='about:blank')

    # Init core returned objects
    desc_obj = dict()
    indicies = set()
    ret_obj  = list()
    parents = dict()

    # Read preferences
    base_url = settings.config('db_api', 'pbdb') + 'taxa/list.json'
    timeout = settings.config('timeout', 'pbdb')
    tax_sys = ['phylum', 'class', 'order', 'family', 'genus']

    # Build parent list
    t0 = time.time()
    payload = dict()
    payload.update(vocab='pbdb', show='full', order='hierarchy')
    payload.update(name=taxon)

    resp = requests.get(base_url, params=payload, timeout=timeout)

    if resp.status_code == 200:
        resp_json = resp.json()
        if 'warnings' in resp_json:
            return connexion.problem(status=400,
                                     title='Bad Request',
                                     detail=str(resp_json['warnings'][0]),
                                     type='about:blank')
        else:
            rec=resp_json['records'][0]
            if rec.get('taxon_rank') == 'kingdom':
                parents.update({'kingdom': rec.get('taxon_name')})
            for rank in tax_sys:
                if rec.get(rank):
                    parents.update({rank: rec.get(rank)})
            if rec.get('taxon_rank') == 'species':
                parents.update({'species': rec.get('taxon_name')})
                #  species = {'species': rec.get('taxon_name')}
                #  rank_inc = {**parents, **species}
            return json.dumps(OrderedDict(parents))
