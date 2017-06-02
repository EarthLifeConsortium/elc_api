"""
RESTful API controller.

Endpoint for scientific publications (also refered to as references).
"""

from flask import request, jsonify
import requests
import time
import re


def format_bibjson(ref):
    """Format BibJSON object."""
    bib = dict()

    # Add basic reference info
    bib.update(type=ref.get('kind'), year=ref.get('year'),
               title=ref.get('title'), citation=ref.get('cite'))

    # Add info specific to the journal or book
    bib.update(journal=[{'name': ref.get('journal'), 'volume': ref.get('vol'),
                         'pages': ref.get('pages'), 'editors': ref.get('editor')}])

    # Add reference locator IDs
    bib.update(identifier=[{'type': 'doi', 'id': ref.get('doi')},
                           {'type': 'db_index', 'id': ref.get('ident')}])

    # Sequentially add authors to the authors block
    bib.update(author=[])
    for author in ref.get('authors'):
        bib['author'].append({'name': author})

    # End subroutine: format_bibjson
    return bib


def format_csv(ref):
    """Format tabular CSV object."""
    bib = dict()
    # End subroutine: format_csv
    return bib


def format_ris(ref):
    """Format RIS object."""
    bib = dict()
    # End subroutine: format_ris
    return bib


def parse_neot_resp(resp, pub_return, desc_obj):
    if resp.status_code == 200:
        resp_json = resp.json()
        if 'data' in resp_json:
            for rec in resp_json['data']:

                # Format the unique database identifier
                pub_id = 'neot:pub:' + str(rec['PublicationID'])

                # Format author fields
                author_list = list()
                if 'Authors' in rec:
                    for author in rec['Authors']:
                        author_list.append(author['ContactName'])

                # Look for a DOI in the citation string
                if 'Citation' in rec:
                    doi = re.search('(?<=\[DOI:\ ).+(?=\])', rec['Citation'])
                    if doi:
                        doi = doi.group()
                else:
                    doi = None

                # Build dictionary of bibliographic fields
                ref = dict()
                ref.update(kind=rec.get('PubType'),
                           year=rec.get('Year'),
                           doi=doi,
                           authors=author_list,
                           ident=pub_id,
                           cite=rec.get('Citation'))

                # Call the appropriate bibliographic formatter
                if format and format.lower() == 'ris':
                    bib_obj = format_ris(ref)
                elif format and format.lower() == 'csv':
                    bib_obj = format_csv(ref)
                else:
                    bib_obj = format_bibjson(ref)

                # Add the fomatted bibliographic reference to the return
                pub_return.append(bib_obj)

    # End subroutine: parse_neot_resp
    return pub_return, desc_obj, len(resp_json['records'])



def parse_pbdb_resp(resp, pub_return, desc_obj):
    if resp.status_code == 200:
        resp_json = resp.json()
        if 'records' in resp_json:
            for rec in resp_json['records']:

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
                author_list = list()
                if 'author1last' in rec:
                    author1 = rec['author1last'].replace(',', '')
                    if 'author1init' in rec:
                        author1 += ', ' + rec['author1init']
                    author_list.append(author1)
                if 'author2last' in rec:
                    author2 = rec['author2last'].replace(',', '')
                    if 'author2init' in rec:
                        author2 += ', ' + rec['author2init']
                    author_list.append(author2)
                if 'otherauthors' in rec:
                    more_authors = rec['otherauthors'].split(', ')
                    for next_author in more_authors:
                        surname = re.search('[A-Z][a-z]+', next_author)
                        name = surname.group() + ', ' + \
                            next_author[0: surname.start()-1]
                        name = name.replace(', and', ', ')
                        author_list.append(name)

                # Format the unique database identifier
                pub_id = 'pbdb:pub:' + str(rec['reference_no'])

                # Build dictionary of bibliographic fields
                ref = dict()
                ref.update(kind=rec.get('publication_type'),
                           title=rec.get('reftitle'),
                           year=rec.get('pubyr'),
                           journal=rec.get('pubtitle'),
                           vol=vol_no,
                           editor=rec.get('editors'),
                           pages=page_range,
                           doi=rec.get('doi'),
                           authors=author_list,
                           ident=pub_id,
                           cite=rec.get('formatted'))

                # Call the appropriate bibliographic formatter
                if format and format.lower() == 'ris':
                    bib_obj = format_ris(ref)
                elif format and format.lower() == 'csv':
                    bib_obj = format_csv(ref)
                else:
                    bib_obj = format_bibjson(ref)

                # Add the fomatted bibliographic reference to the return
                pub_return.append(bib_obj)

    # End subroutine: parse_pbdb_resp
    return pub_return, desc_obj, len(resp_json['records'])


def pub(idnumbers=None, format=None):
    """Return primary reference data in BibJSON, CSV or RIS format."""
    # Initialization and parameter checks
    if request.args == {}:
        return jsonify(status_code=400, error='No parameters provided.')
    desc_obj = dict()
    pub_return = list()
    pbdb_occs = list()
    pbdb_locs = list()
    neot_occs = list()
    neot_locs = list()

    # Parse database and dataset id numbers
    print(idnumbers)
    if idnumbers:
        for id in idnumbers:
            print(id)
            database= re.search('^\w+(?=:)', id).group()
            datatype = re.search('(?<=:).+(?=:)', id).group()
            id_num = int(re.search('\d+$', id).group())

            if database.lower() == 'neot':
                if datatype.lower() == 'occ':
                    neot_occs.append(id_num)
                elif datatype.lower() == 'loc':
                    neot_locs.append(id_num)
                else:
                    return jsonify(status_code=400,
                                   error='ID error: datatype.')
            elif database.lower() == 'pbdb':
                if datatype.lower() == 'occ':
                    pbdb_occs.append(id_num)
                elif datatype.lower() == 'loc':
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
    payload = dict()
    api_calls = list()
    rec_count = 0

    # Issue a GET request for references associated with occurrences
    if neot_occs:
        base_url = ''
        payload.update(occid='')
        resp = requests.get(base_url, params=payload, timeout=5)
        api_calls.append(resp.url)
        pub_return, desc_obj, cnt = parse_neot_resp(resp, pub_return, desc_obj)
        rec_count = rec_count + cnt

    # Issue a GET request for references associated with locales
    if neot_locs:
        base_url = 'http://api.neotomadb.org/v1/data/publications'
        payload.update(datasetid=neot_locs)
        resp = requests.get(base_url, params=payload, timeout=5)
        api_calls.append(resp.url)
        pub_return, desc_obj, cnt = parse_neot_resp(resp, pub_return, desc_obj)
        rec_count = rec_count + cnt

    # Build the JSON description object
    t1 = round(time.time()-t0, 3)
    desc_obj.update(neotoma={'response_time': t1,
                             'status_code': resp.status_code,
                             'subqueries': api_calls,
                             'record_count': rec_count})

    #
    # Query the Paleobiology Database (Publications)
    #
    t0 = time.time()
    payload = dict()
    payload.update(vocab='pbdb', show='both')
    api_calls = list()
    rec_count = 0

    # Issue a GET request for references associated with occurrences
    if pbdb_occs:
        base_url = 'http://paleobiodb.org/data1.2/occs/refs.json'
        payload.update(occ_id=pbdb_occs)
        resp = requests.get(base_url, params=payload, timeout=5)
        api_calls.append(resp.url)
        pub_return, desc_obj, cnt = parse_pbdb_resp(resp, pub_return, desc_obj)
        rec_count = rec_count + cnt
    
    # Issue a GET request for references associated with locales
    if pbdb_locs:
        base_url = 'http://paleobiodb.org/data1.2/colls/refs.json'
        payload.update(coll_id=pbdb_locs)
        resp = requests.get(base_url, params=payload, timeout=5)
        api_calls.append(resp.url)
        pub_return, desc_obj, cnt = parse_pbdb_resp(resp, pub_return, desc_obj)
        rec_count = rec_count + cnt

    # Build the JSON description object
    t1 = round(time.time()-t0, 3)
    desc_obj.update(pbdb={'response_time': t1,
                          'status_code': resp.status_code,
                          'subqueries': api_calls,
                          'record_count': rec_count})

    # Composite response
    return jsonify(description=desc_obj, records=pub_return)
