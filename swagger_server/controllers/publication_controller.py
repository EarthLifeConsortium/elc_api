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

    # Query the Neotoma Database (Publications)
    t0 = time.time()
    payload = dict()








    # Query the Paleobiology Database (Publications)
    t0 = time.time()
    payload = dict()
    payload.update(vocab='pbdb')

    if occid:
        pbdb_base = 'http://paleobiodb.org/data1.2/occs/refs.json'
        payload.update(occ_id=occid)
    elif siteid:
        pbdb_base = 'http://paleobiodb.org/data1.2/colls/refs.json'
        payload.update(coll_id=siteid)
    else:
        return jsonify(status_code=400,
                       error='Specify occurrence ID or site ID.')

    pbdb_res = requests.get(pbdb_base, params=payload, timeout=None)

    if pbdb_res.status_code == 200:
        pbdb_json = pbdb_res.json()
        if 'records' in pbdb_json:
            for pub in pbdb_json['records']:
                pub_id = 'pbdb:pub:' + str(pub['reference_no'])

                bibjson = dict()
                (kind,title,year,journal,vol,pages,doi,
                            author1,author2,editors) = [None]*10
                other_authors = list()

                if 'publication_type' in pub:
                    kind = pub['publication_type']
                if 'reftitle' in pub:
                    title = pub['reftitle']
                if 'pubyr' in pub:
                    year = pub['pubyr']
                if 'pubtitle' in pub:
                    journal = pub['pubtitle']
                if 'pubvol' in pub:
                    vol = pub['pubvol']
                    if 'pubno' in pub:
                        vol = pub['pubno'] + ' (' + vol + ')'
                if 'editors' in pub:
                    editors = pub['editors']
                if 'firstpage' in pub and 'lastpage' in pub:
                    pages = pub['firstpage'] + '-' + pub['lastpage']
                if 'doi' in pub:
                    doi = pub['doi']
                if 'author1last' in pub:
                    author1 = pub['author1last']
                    if 'author1init' in pub:
                        author1 += ', ' + pub['author1init']
                if 'author2last' in pub:
                    author2 = pub['author2last']
                    if 'author2init' in pub:
                        author2 += ', ' + pub['author2init']
                if 'otherauthors' in pub:
                    other_authors = pub['otherauthors'].split(', ')

                bibjson.update(type=kind, year=year, title=title)
                bibjson.update(author=[{'name':author1}])
                if author2:
                    bibjson['author'].append({'name':author2})
                for next_author in other_authors:
                    surname = re.search('[A-Z][a-z]+', next_author)
                    fullname = surname.group() + ', ' + \
                               next_author[0:surname.start()-1]
                    bibjson['author'].append({'name':fullname})
                bibjson.update(journal=[{'name':journal,'volume':vol,
                                         'pages':pages,'editors':editors}])
                bibjson.update(identifier=[{'type':'doi', 'id':doi},
                                           {'type':'database', 'id':pub_id}])

                pub_return.append(bibjson)

            t1 = round(time.time()-t0, 5)
            desc_obj.update(pbdb_time=t1)
            desc_obj.update(pbdb_url=pbdb_res.url)
            desc_obj.update(pbdb_pubs=len(pbdb_json['records']))

    # Composite response
    return jsonify(description=desc_obj, records=pub_return)
