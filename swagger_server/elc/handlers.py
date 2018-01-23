"""Custom handlers for decoding each database return."""


def occurrence(resp_json, return_obj, options, db):
    """
    Extract necessary data from the subquery.

    :arg db: Database name
    :type db: str
    :arg resp_json: Database subquery responce object
    :type resp_json: dict
    :arg return_obj: List of data objects to be appended and returned
    :type return_obj: list (of dicts)

    """
    from ..elc import aux

    # Custom decoder for Neotoma Paleoecology Database response

    if db == 'neotoma':

        factor = aux.set_age_scaler(options=options, db='neotoma')

        for rec in resp_json.get('data', []):

            data = dict()

            data.update(occ_id='neot:occ:{0:d}'
                        .format(rec.get('sampleid', 0)))

            if rec.get('taxon'):
                data.update(taxon=rec.get('taxon').get('taxonname'))
                data.update(taxon_id='neot:txn:{0:d}'
                            .format(rec.get('taxon').get('taxonid', 0)))

            if rec.get('ages'):
                if rec.get('ages').get('ageolder'):
                    age = rec.get('ages').get('ageolder') / factor
                    data.update(max_age=round(age, 5))
                    age = rec.get('ages').get('ageyounger') / factor
                    data.update(min_age=round(age, 5))
                else:
                    age = rec.get('ages').get('age') / factor
                    data.update(max_age=round(age, 5))
                    data.update(min_age=round(age, 5))

            if rec.get('site'):
                data.update(source=rec.get('site').get('database'))
                data.update(data_type=rec.get('site').get('datasettype'))
                if rec.get('site').get('datasetid'):
                    data.update(locale_id='neot:dst:{0:d}'
                                .format(rec.get('site').get('datasetid', 0)))

            # !!! geog stuff here
            return_obj.append(data)

        return return_obj

    # Custom decoder for the Paleobiology Database response

    elif db == 'pbdb':

        factor = aux.set_age_scaler(options=options, db='pbdb')

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

    # Add additional database custom handler below

    else:
        msg = 'Database suport lacking: {0:s}'.format(db)
        raise ValueError(501, msg)
