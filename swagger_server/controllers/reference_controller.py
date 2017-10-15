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


def format_bibjson(reference):
    """Format BibJSON object."""
    bib = dict()

    # Add basic reference info
    bib.update(type=reference.get('kind'), year=reference.get('year'),
               title=reference.get('title'), citation=reference.get('cite'))

    # Add info specific to the journal or book
    bib.update(journal=[{'name': reference.get('journal'),
                         'volume': reference.get('vol'),
                         'pages': reference.get('pages'),
                         'editors': reference.get('editor')}])

    # Add reference locator IDs
    bib.update(identifier=[{'type': 'doi', 'id': reference.get('doi')},
                           {'type': 'db_index', 'id': reference.get('ident')}])

    # Sequentially add authors to the authors block
    bib.update(author=[])
    for author in reference.get('authors'):
        bib['author'].append({'name': author})

    # End subroutine: format_bibjson
    return bib


def format_csv(reference):
    """Format tabular CSV object."""
    bib = dict()
    # End subroutine: format_csv
    return bib


def format_ris(reference):
    """Format RIS object."""
    bib = dict()
    # End subroutine: format_ris
    return bib


def format_handler(reference, pub_return, format):
    """Call the appropriate bibliographic formatter."""
    if format and format.lower() is 'ris':
        bib_obj = format_ris(reference)
    elif format and format.lower() is 'csv':
        bib_obj = format_csv(reference)
    else:
        bib_obj = format_bibjson(reference)

    # Add the fomatted bibliographic reference to the return
    pub_return.append(bib_obj)

    # End subroutine: format_handler
    return pub_return


def parse_neot_resp(resp, pub_return, format):
    """Reformat data from the Neotoma API call."""
    if resp.status_code == 200:
        resp_json = resp.json()
        if 'data' in resp_json:
            for rec in resp_json['data']:

                # Format the unique database identifier
                pub_id = 'neot:pub:' + str(rec.get('PublicationID'))

                # Format author fields
                author_list = list()
                if 'Authors' in rec:
                    for author in rec.get('Authors'):
                        author_list.append(author['ContactName'])

                # Look for a DOI in the citation string
                if 'Citation' in rec:
                    doi = re.search('(?<=\[DOI:\ ).+(?=\])', rec.get('Citation'))
                    if doi:
                        doi = doi.group()
                else:
                    doi = None

                # Build dictionary of bibliographic fields
                reference = dict()
                reference.update(kind=rec.get('PubType'),
                                 year=rec.get('Year'),
                                 doi=doi,
                                 authors=author_list,
                                 ident=pub_id,
                                 cite=rec.get('Citation'))

                # Format and append parsed record
                pub_return = format_handler(reference, pub_return, format)

    # End subroutine: parse_neot_resp
    return len(resp_json['data'])


def parse_pbdb_resp(resp, pub_return, format):
    """Reformat data from the Neotoma API call."""
    if resp.status_code == 200:
        resp_json = resp.json()
        if 'records' in resp_json:
            for rec in resp_json['records']:

                # Format publication "volume(issue)"
                if 'pubno' in rec:
                    vol_no = rec.get('pubno')
                    if 'pubvol' in rec:
                        vol_no = rec.get('pubvol') + ' (' + vol_no + ')'
                else:
                    vol_no = None

                # Format publication "first-last" page range
                if 'firstpage' in rec:
                    page_range = rec.get('firstpage')
                    if 'lastpage' in rec:
                        page_range = page_range + '-' + rec.get('lastpage')
                else:
                    page_range = None

                # Format author fields
                author_list = list()
                if 'author1last' in rec:
                    author1 = rec.get('author1last').replace(',', '')
                    if 'author1init' in rec:
                        author1 += ', ' + rec.get('author1init')
                    author_list.append(author1)
                if 'author2last' in rec:
                    author2 = rec.get('author2last').replace(',', '')
                    if 'author2init' in rec:
                        author2 += ', ' + rec.get('author2init')
                    author_list.append(author2)
                if 'otherauthors' in rec:
                    more_authors = rec.get('otherauthors').split(', ')
                    for next_author in more_authors:
                        surname = re.search('[A-Z][a-z]+', next_author)
                        name = surname.group() + ', ' + \
                            next_author[0: surname.start()-1]
                        name = name.replace(', and', ', ')
                        author_list.append(name)

                # Format the unique database identifier
                pub_id = 'pbdb:ref:' + str(rec.get('reference_no'))

                # Build dictionary of bibliographic fields
                reference = dict()
                reference.update(kind=rec.get('publication_type'),
                                 title=rec.get('referencetitle'),
                                 year=rec.get('pubyr'),
                                 journal=rec.get('pubtitle'),
                                 vol=vol_no,
                                 editor=rec.get('editors'),
                                 pages=page_range,
                                 doi=rec.get('doi'),
                                 authors=author_list,
                                 ident=pub_id,
                                 cite=rec.get('formatted'))

                # Format and append parsed record
                pub_return = format_handler(reference, pub_return, format)

    # End subroutine: parse_pbdb_resp
    return len(resp_json['records'])


def ref(idnumbers=None, format=None):
    """Return primary reference data in BibJSON, CSV or RIS format."""
    # Initialization and parameter checks
    if not bool(request.args):
        return connexion.problem(status=400,
                                 title='Bad Request',
                                 detail='No parameters provided.',
                                 type='about:blank')
    desc_obj = dict()
    pub_return = list()
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

        count = parse_neot_resp(resp, pub_return, format)
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

        count = parse_neot_resp(resp, pub_return, format)
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

        count = parse_pbdb_resp(resp, pub_return, format)
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

        count = parse_pbdb_resp(resp, pub_return, format)
        tot_count = tot_count + count

    # Build the JSON description object
    t1 = round(time.time()-t0, 3)
    desc_obj.update(pbdb={'response_time': t1,
                          'status_codes': status_codes,
                          'subqueries': api_calls,
                          'record_count': tot_count})

    # Composite response
    return jsonify(description=desc_obj, records=pub_return)
