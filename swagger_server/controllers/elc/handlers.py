"""Custom handlers for decoding each database return."""

def occurrence(db, resp_json):
    """Extract necessary data from the subquery."""

    if db == 'neotoma':

        return_obj = list()

        if 'data' in resp_json:
            for rec in resp_json['data']:
                data = dict()

                occ_id = 'occ:neot:{0:s}'.format(str(rec.get('sampleid')))

                taxon = taxon=rec['taxon']['taxonname']

                data.update(occ_id=occ_id,
                            taxon=taxon)

                return_obj.append(data)

        else:
            msg = 'No data records found: {0:s}'.format(db)
            raise ValueError(204, msg)

        return return_obj





    elif db == 'pbdb':

        return_obj = list()

        if 'records' in resp_json:
            for rec in resp_json:
                data = dict()

                occ_id = 'occ:pbdb:{0:s}'.format(str(rec.get(occurrence_no)))

        return return_obj

    else:
    msg = 'Database suport lacking: {0:s}'.format(db)
        raise ValueError(501, msg)
