"""Custom handlers for decoding each database return."""


def occurrence(db, resp_json):
    """Extract necessary data from the subquery."""
    if db == 'neotoma':

        return_obj = list()

        for rec in resp_json.get('data', []):

            data = dict()

            data.update(occ_id='occ:neot:{0:d}'
                        .format(rec.get('sampleid', 0)))

            if rec.get('taxon'):
                data.update(taxon=rec.get('taxon').get('taxonname'))
                data.update(taxonid=rec.get('taxon').get('taxonid'))

            if rec.get('ages'):
                if rec.get('ages').get('age'):
                    data.update(max_age=rec.get('ages')['age'])
                    data.update(min_age=rec.get('ages')['age'])
                else:
                    data.update(max_age=rec.get('ages')['ageolder'])
                    data.update(min_age=rec.get('ages')['ageyounger'])

            return_obj.append(data)

        return return_obj

    elif db == 'pbdb':

        return_obj = list()

        for rec in resp_json.get('records', []):

            data = dict()

            data.update(occ_id='occ:pbdb:{0:d}'
                        .format(rec.get('occurrence_no', 0)))

            return_obj.append(data)

        return return_obj

    else:
        msg = 'Database suport lacking: {0:s}'.format(db)
        raise ValueError(501, msg)
