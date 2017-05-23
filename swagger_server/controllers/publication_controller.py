"""
RESTful API controller.

Endpoint for queries on occurrence and site reference publications.
"""

# import connexion
# from swagger_server.models.error_model import ErrorModel
# from swagger_server.models.publication import Publication
# from datetime import date, datetime
# from typing import List, Dict
# from six import iteritems
# from ..util import deserialize_date, deserialize_datetime
from flask import request, jsonify
import requests
import time
import re


def pub(occid=None, siteid=None, format=None):
    """
    Return occurrence identifiers from Neotoma and PBDB.

    Format= bibjson or ris.
    """
    # Initialization and parameter checks
    if request.args == {}:
        return jsonify(status_code=400, error='No parameters provided.')
    if occid and siteid:
        return jsonify(status_code=400,
                       error='Specify only occurrence ID or site ID not both.')

    desc_obj = dict()
    pub_return = list()
    ris_format = False

    if format and format.lower() == 'ris':
        ris_format = True

    #
    # Query the Neotoma Database (Publications)
    #

    #
    # Query the Paleobiology Database (Publications)
    #
    t0 = time.time()
    payload = dict()
    payload.update(vocab='pbdb', show='both')

    # Select the appropriate URI for occs or sites/colls
    if occid:
        base_url = 'http://paleobiodb.org/data1.2/occs/refs.json'
        payload.update(occ_id=occid)
    elif siteid:
        base_url = 'http://paleobiodb.org/data1.2/colls/refs.json'
        payload.update(coll_id=siteid)
    else:
        return jsonify(status_code=400,
                       error='Specify occurrence ID or site ID.')

    # Issue GET request to database API
    res = requests.get(base_url, params=payload, timeout=None)

    if res.status_code == 200:
        res_json = res.json()
        if 'records' in res_json:
            for rec in res_json['records']:

                # Format publication "volume(issue)"
                if 'pubvol' in rec:
                    vol_no = rec['pubvol']
                    if 'pubno' in rec:
                        vol_no = rec['pubno'] + ' (' + vol_no + ')'
                else:
                    vol_no = None

                # Format publication "first-last" page range
                if 'firstpage' in rec:
                    page_range = rec['firstpage']
                    if 'lastpage' in rec:
                        page_range = page_range + '-' + rec['lastpage']
                else:
                    page_range = None

                # Format author fields
                if 'author1last' in rec:
                    author_1 = rec['author1last']
                    if 'author1init' in rec:
                        author_1 += ', ' + rec['author1init']
                else:
                    author_1 = None
                if 'author2last' in rec:
                    author_2 = rec['author2last']
                    if 'author2init' in rec:
                        author_2 += ', ' + rec['author2init']
                else:
                    author_2 = None
                if 'otherauthors' in rec:
                    author_other = rec['otherauthors'].split(', ')
                else:
                    author_other = None

                # Format the unique database identifier
                pub_id = 'pbdb:pub:' + str(pub['reference_no'])

                # Build dictionary of bibliographic fields
                pub = dict()
                pub.update(kind=rec.get('publication_type'),
                           title=rec.get('reftitle'),
                           year=rec.get('pubyr'),
                           journal=rec.get('pubtitle'),
                           vol=vol_no,
                           editors=rec.get('editors'),
                           pages=page_range,
                           doi=rec.get('doi'),
                           auth1=author_1,
                           auth2=author_2,
                           auth3=author_other,
                           ident=pub_id,
                           cite=bibliographicCitation)

                # Format the bibliographic refernce and add it to the return 
                bib_obj = format_bibjson(pub)
                pub_return.append(bibjson)

            t1 = round(time.time()-t0, 5)
            desc_obj.update(pbdb_time=t1)
            desc_obj.update(pbdb_url=res.url)
            desc_obj.update(pbdb_pubs=len(res_json['records']))

    # Composite response
    return jsonify(description=desc_obj, records=pub_return)
