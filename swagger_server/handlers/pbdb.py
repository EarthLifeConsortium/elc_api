"""Custom decoder for the Paleobiology Database response."""


def locales(resp_json, return_obj, options):
    """Extract locale data from the subquery."""
    from ..elc import ages

    factor = ages.set_age_scaler(options=options, db='pbdb')

    #  import pdb; pdb.set_trace()


    for rec in resp_json.get('records', []):

        data = dict()

        data.update(locale_id='pbdb:{0:s}'.format(rec.get('oid', 'col:0')))
        data.update(doi=None)
        data.update(locale_name=rec.get(

        data.update(source='pbdb:{0:s}'.format(rec.get('rid', 'ref:0')))
        #  data.update(locale_name=rec.get('nam'))

        #  data.update(max_age=round(rec.get('eag') / factor, 4))
        #  data.update(min_age=round(rec.get('lag') / factor, 4))

        #  data.update(data_type=rec.get('cct', 'general faunal/floral'))

        # !!! geog stuff here

        return_obj.append(data)

    return return_obj


def occurrences(resp_json, return_obj, options):
    """Extract occurrence data from the subquery."""
    from ..elc import ages

    factor = ages.set_age_scaler(options=options, db='pbdb')

    for rec in resp_json.get('records', []):

        data = dict()

        data.update(occ_id='pbdb:{0:s}'.format(rec.get('oid', 'occ:0')))

        data.update(taxon=rec.get('tna'))
        data.update(taxon_id='pbdb:{0:s}'.format(rec.get('tid', 'txn:0')))

        data.update(max_age=round(rec.get('eag') / factor, 4))
        data.update(min_age=round(rec.get('lag') / factor, 4))

        data.update(source='pbdb:{0:s}'.format(rec.get('rid', 'ref:0')))
        data.update(data_type=rec.get('cct', 'general faunal/floral'))
        data.update(locale_id='pbdb:{0:s}'.format(rec.get('cid', 'col:0')))

        # !!! geog stuff here

        return_obj.append(data)

    return return_obj


def references(resp, ret_obj, format):
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
                ret_obj = format_handler(reference, ret_obj, format)

    # End subroutine: parse_pbdb_resp
    return len(resp_json['records'])

