"""Custom decoder for the Paleobiology Database response."""


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

    for rec in resp_json.get('records', []):

        data = dict()

        data.update(occ_id='pbdb:{0:s}'.format(rec.get('oid', 'occ:0')))

        data.update(taxon=rec.get('tna'))
        data.update(taxon_id='pbdb:{0:s}'.format(rec.get('tid', 'txn:0')))

        data.update(max_age=round(rec.get('eag') / options.age_fac, 4))
        data.update(min_age=round(rec.get('lag') / options.age_fac, 4))

        data.update(source='pbdb:{0:s}'.format(rec.get('rid', 'ref:0')))
        data.update(data_type=rec.get('cct', 'general faunal/floral'))
        data.update(locale_id='pbdb:{0:s}'.format(rec.get('cid', 'col:0')))

        # !!! geog stuff here

        return_obj.append(data)

    return return_obj
