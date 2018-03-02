"""Custom decoder for Neotoma Paleoecology Database response."""


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
