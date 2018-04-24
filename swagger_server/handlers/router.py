"""Call approproiate custom response handler for database:api_route."""


def response_decode(resp_json, return_obj, options, db, endpoint):
    """
    Extract necessary data from the subquery.

    :arg db: Database name
    :type db: str
    :arg resp_json: Database subquery responce object
    :type resp_json: dict
    :arg return_obj: List of data objects to be appended and returned
    :type return_obj: list (of dicts)
    :arg endpoint: Route to follow
    :type endpoint: str
    """
    from ..handlers import neotoma, pbdb

    if db == 'neotoma':
        if endpoint == 'occ':
            return neotoma.occurrences(resp_json, return_obj, options)
        if endpoint == 'loc':
            return neotoma.locales(resp_json, return_obj, options)
        if endpoint == 'ref':
            return neotoma.references(resp_json, return_obj, options)

    if db == 'pbdb':
        if endpoint == 'occ':
            return pbdb.occurrences(resp_json, return_obj, options)
        if endpoint == 'loc':
            return pbdb.locales(resp_json, return_obj, options)
        if endpoint == 'ref':
            return pbdb.references(resp_json, return_obj, options)

    # Add additional database custom handler here

    else:
        msg = 'Database suport lacking: {0:s}'.format(db)
        raise ValueError(501, msg)
