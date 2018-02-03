"""Call approproiate custom response handler for database:endpoint."""


def decode_occs(resp_json, return_obj, options, db):
    """
    Extract necessary data from the subquery.

    :arg db: Database name
    :type db: str
    :arg resp_json: Database subquery responce object
    :type resp_json: dict
    :arg return_obj: List of data objects to be appended and returned
    :type return_obj: list (of dicts)
    """
    from ..handlers import neotoma, pbdb

    if db == 'neotoma':
        return neotoma.occurrences(resp_json, return_obj, options)
    if db == 'pbdb':
        return pbdb.occurrences(resp_json, return_obj, options)
    # Add additional database custom handler here
    else:
        msg = 'Database suport lacking: {0:s}'.format(db)
        raise ValueError(501, msg)
