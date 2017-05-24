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
    print(ref)
    bib = dict()

    # Add basic reference info
    bib.update(type=ref['kind'], year=ref['year'],
               title=ref['title'], citation=ref['cite'])

    # Add info specific to the journal or book
    bib.update(journal=[{'name': ref['journal'], 'volume': ref['vol'],
                         'pages': ref['pages'], 'editors': ref['editor']}])

    # Add reference locator IDs
    bib.update(identifier=[{'type': 'doi', 'id': ref['doi']},
                           {'type': 'database', 'id': ref['ident']}])

    # Sequentially add authors to the authors block
    bib.update(author=[{'name': ref['auth1']}])
    if ref['auth2']:
        bib['author'].append({'name': ref['auth2']})
    # Parse other authors and reverse the initials and surname
    if ref['auth3']:
        print('-----> ', ref['auth3'])
        other_authors = ref['auth3'].split(', ')
        for next_author in other_authors:
            surname = re.search('[A-Z][a-z]+', next_author)
            name = surname.group() + ', ' + next_author[0: surname.start()-1]
            bib['author'].append({'name': name})

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


def pub(occid=None, siteid=None, format=None):
    """Return primary reference data in BibJSON, CSV or RIS format."""
    # Initialization and parameter checks
    desc_obj = dict()
    pub_return = list()
    if request.args == {}:
        return jsonify(status_code=400, error='No parameters provided.')
    if occid and siteid:
        return jsonify(status_code=400,
                       error='Specify only occurrence ID or site ID not both.')

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
                           auth1=author_1,
                           auth2=author_2,
                           auth3=author_other,
                           ident=pub_id,
                           cite=rec.get('bibliographicCitation'))

                # Call the appropriate bibliographic formatter
                if format and format.lower() == 'ris':
                    bib_obj = format_ris(ref)
                elif format and format.lower() == 'csv':
                    bib_obj = format_csv(ref)
                else:
                    bib_obj = format_bibjson(ref)

                # Add the fomatted bibliographic reference to the return
                pub_return.append(bib_obj)

            # Build the JSON description object
            t1 = round(time.time()-t0, 5)
            desc_obj.update(pbdb_time=t1)
            desc_obj.update(pbdb_url=res.url)
            desc_obj.update(pbdb_pubs=len(res_json['records']))

    # Composite response
    return jsonify(description=desc_obj, records=pub_return)
