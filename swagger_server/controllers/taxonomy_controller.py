"""
RESTful API controller.

Endpoint for miscelaneous queries on specific species taxonomy.
"""

import time
from connexion import problem
import json
from flask import request, jsonify, Response
from .ControllerCommon import params, settings, formatters, aux

def tax(taxon=None, includelower=None, hierarchy=None):
    """
    Return taxonomic hierarchy and subtaxa in various formats.

    :arg format: json, itis or csv formatted return
    """
    # Parameter checks
    if not bool(request.args):
        return problem(status=400,
                       title='Bad Request',
                       detail='No parameters provided.',
                       type='about:blank')

    # Init core returned objects
    desc_obj = dict()
    indicies = set()
    ret_obj  = list()

    t0 = time.time()

    # Build parent list
    try:
        parents = aux.get_parents(taxon)
    except ValueError as err:
        return problem(status=err.args[0],
                       title=err.args[1],
                       detail=err.args[2],
                       type='about:blank')

    return json.dumps(parents)

    # Build subtaxa list
    try:
        subtaxa = aux.get_subtaxa(taxon)
    except ValueError as err:
        return problem(status=err.args[0],
                       title=err.args[1],
                       detail=err.args[2],
                       type='about:blank')

    #  return formatters.type_plain(subtaxa)
