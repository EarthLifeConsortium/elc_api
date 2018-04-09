"""Custom decoder for Neotoma Paleoecology Database response."""


def locales(resp_json, return_obj, options):
    """Extract locale data from the subquery."""
    from ..elc import ages

    factor = ages.set_age_scaler(options=options, db='pbdb')

    for rec in resp_json.get('data', []):

        for dataset in rec.get('dataset'):
            data = dict()

            data.update(locale_id='neot:dst:{0:d}'
                        .format(dataset.get('datasetid', 0)))
            data.update(doi=dataset.get('doi'))

            data.update(source=dataset.get('database'))

            return_obj.append(data)

    return return_obj


def occurrences(resp_json, return_obj, options):
    """
    Extract necessary data from the subquery.

    :arg db: Database name
    :type db: str
    :arg resp_json: Database subquery responce object
    :type resp_json: dict
    :arg return_obj: List of data objects to be appended and returned
    :type return_obj: list (of dicts)
    """
    from ..elc import ages

    factor = ages.set_age_scaler(options=options, db='neotoma')

    for rec in resp_json.get('data', []):

        data = dict()

        data.update(occ_id='neot:occ:{0:d}'.format(rec.get('sampleid', 0)))

        if rec.get('sample'):

            data.update(taxon=rec.get('sample').get('taxonname'))
            data.update(taxon_id='neot:txn:{0:d}'
                        .format(rec.get('sample').get('taxonid', 0)))

        if rec.get('age'):

            def choose(x, y): return x or y

            old = choose(rec.get('age').get('ageolder'),
                         rec.get('age').get('age'))
            if old and old >= 0:
                data.update(max_age=round(old / factor, 5))
            else:
                data.update(max_age=None)

            yng = choose(rec.get('age').get('ageyounger'),
                         rec.get('age').get('age'))
            if yng and yng >= 0:
                data.update(min_age=round(yng / factor, 5))
            else:
                data.update(min_age=None)

        if rec.get('site'):

            data.update(source=rec.get('site').get('database'))
            data.update(data_type=rec.get('site').get('datasettype'))
            if rec.get('site').get('datasetid'):
                data.update(locale_id='neot:dst:{0:d}'
                            .format(rec.get('site').get('datasetid', 0)))

        # !!! geog stuff here
        return_obj.append(data)

    return return_obj


def references(resp, ret_obj, format):
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
                ret_obj = format_handler(reference, ret_obj, format)

    # End subroutine: parse_neot_resp
    return len(resp_json['data'])

