"""
RESTful API controller.

Endpoint for scientific references in the databases.
Neotoma referes to these as publications whereas in PBDB publications are
end user products that cite the database itself as a primary reference.
"""

import requests
import time
import re
import connexion
from flask import request, jsonify


def format_handler(reference, ret_obj, format):
    """Call the appropriate bibliographic formatter."""
    if format and format.lower() is 'ris':
        bib_obj = format_ris(reference)
    elif format and format.lower() is 'csv':
        bib_obj = format_csv(reference)
    else:
        bib_obj = format_bibjson(reference)

    # Add the fomatted bibliographic reference to the return
    ret_obj.append(bib_obj)

    # End subroutine: format_handler
    return ret_obj




def ref(idnumbers=None, format=None):
    """Return primary reference data in BibJSON, CSV or RIS format."""
    # Initialization and parameter checks
    if not bool(request.args):
        return connexion.problem(status=400,
                                 title='Bad Request',
                                 detail='No parameters provided.',
                                 type='about:blank')
    desc_obj = dict()
    ret_obj = list()
    pbdb_occs = list()
    pbdb_locs = list()
    neot_occs = list()
    neot_locs = list()

    # Parse database and dataset id numbers
    if idnumbers:
        for id in idnumbers:
            database = re.search('^\w+(?=:)', id).group()
            datatype = re.search('(?<=:).+(?=:)', id).group()
            id_num = int(re.search('\d+$', id).group())

            if database.lower() == 'neot':
                if datatype.lower() == 'occ':
                    neot_occs.append(id_num)
                elif datatype.lower() == 'dst':
                    neot_locs.append(id_num)
                else:
                    return jsonify(status_code=400,
                                   error='ID error: datatype.')
            elif database.lower() == 'pbdb':
                if datatype.lower() == 'occ':
                    pbdb_occs.append(id_num)
                elif datatype.lower() == 'col':
                    pbdb_locs.append(id_num)
                else:
                    return jsonify(status_code=400,
                                   error='ID error: Datatype syntax.')
            else:
                return jsonify(status_code=400,
                               error='ID error: Database name syntax.')
    else:
        return jsonify(status_code=400,
                       error='ID error: Missing ID number.')

    #
    # Query the Neotoma Database (Publications)
    #
    t0 = time.time()
    api_calls = list()
    status_codes = list()
    tot_count = 0
    count = 0

    # Issue a GET request for references associated with occurrences
    if neot_occs:
        payload = dict()
        base_url = ''
        id_list = ','.join(str(element) for element in neot_occs)
        payload.update(occid=id_list)
        resp = requests.get(base_url, params=payload, timeout=5)
        api_calls.append(resp.url)
        status_codes.append(resp.status_code)

        count = parse_neot_resp(resp, ret_obj, format)
        tot_count = tot_count + count

    # Issue a GET request for references associated with locales
    if neot_locs:
        payload = dict()
        base_url = 'http://api.neotomadb.org/v1/data/publications'
        id_list = ','.join(str(element) for element in neot_locs)
        payload.update(datasetid=id_list)
        resp = requests.get(base_url, params=payload, timeout=5)
        api_calls.append(resp.url)
        status_codes.append(resp.status_code)

        count = parse_neot_resp(resp, ret_obj, format)
        tot_count = tot_count + count

    # Build the JSON description object
    t1 = round(time.time()-t0, 3)
    desc_obj.update(neotoma={'response_time': t1,
                             'status_codes': status_codes,
                             'subqueries': api_calls,
                             'record_count': tot_count})

    #
    # Query the Paleobiology Database (Publications)
    #
    t0 = time.time()
    api_calls = list()
    status_codes = list()
    tot_count = 0

    # Issue a GET request for references associated with occurrences
    if pbdb_occs:
        payload = dict()
        payload.update(vocab='pbdb', show='both')
        base_url = 'http://paleobiodb.org/data1.2/occs/refs.json'
        id_list = ','.join(str(element) for element in pbdb_occs)
        payload.update(occ_id=id_list)
        resp = requests.get(base_url, params=payload, timeout=5)
        api_calls.append(resp.url)
        status_codes.append(resp.status_code)

        count = parse_pbdb_resp(resp, ret_obj, format)
        tot_count = tot_count + count

    # Issue a GET request for references associated with locales
    if pbdb_locs:
        payload = dict()
        payload.update(vocab='pbdb', show='both')
        base_url = 'http://paleobiodb.org/data1.2/colls/refs.json'
        id_list = ','.join(str(element) for element in pbdb_locs)
        payload.update(coll_id=id_list)
        resp = requests.get(base_url, params=payload, timeout=5)
        api_calls.append(resp.url)
        status_codes.append(resp.status_code)

        count = parse_pbdb_resp(resp, ret_obj, format)
        tot_count = tot_count + count

    # Build the JSON description object
    t1 = round(time.time()-t0, 3)
    desc_obj.update(pbdb={'response_time': t1,
                          'status_codes': status_codes,
                          'subqueries': api_calls,
                          'record_count': tot_count})

    # Composite response
    return jsonify(description=desc_obj, records=ret_obj)
