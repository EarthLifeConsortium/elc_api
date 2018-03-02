"""Common parameter parsing functions for the API controllers."""


def set_options(req_args, endpoint):
    """Return a dictionary with runtime options and config."""
    from ..elc import config
    from ast import literal_eval

    # Add aditional formats and controls below (default is param[0])
    spec = dict()
    spec.update(misc=['json'])
    spec.update(occ=['json', 'csv'])
    spec.update(loc=['json', 'csv'])
    spec.update(tax=['json', 'csv'])
    spec.update(ref=['bibjson', 'ris', 'itis'])
    spec.update(show=['all', 'poll', 'idx'])
    spec.update(age=['ma', 'ka', 'yr'])
    spec.update(geog=['paleo', 'modern'])

    # Runtime options
    options = dict()

    # Response format
    if 'output' in req_args.keys():
        if req_args.get('output').lower() in spec.get(endpoint):
            options.update(output=req_args.get('output'))
        else:
            msg = 'Allowable formats: {0:s}'.format(str(spec.get(endpoint)))
            raise ValueError(400, msg)
    else:
        options.update(output=spec.get(endpoint)[0])

    # Response includes
    if 'show' in req_args.keys():
        if req_args.get('show').lower() in spec.get('show'):
            options.update(show=req_args.get('show'))
        else:
            msg = 'Allowable show args: {0:s}'.format(str(spec.get('show')))
            raise ValueError(400, msg)
    else:
        options.update(show=spec.get('show')[0])

    # Age measurement units
    if 'ageunits' in req_args.keys():
        if req_args.get('ageunits').lower() in spec.get('age'):
            options.update(ageunits=req_args.get('ageunits'))
        else:
            msg = 'Allowable age units: {0:s}'.format(str(spec.get('age')))
            raise ValueError(400, msg)
    else:
        if config.get('default', 'ageunits') in spec.get('age'):
            options.update(ageunits=config.get('default', 'ageunits'))
        else:
            msg = 'Config: ageunits not in {0:s}'.format(str(spec.get('age')))
            raise ValueError(500, msg)

    # Geographic coodinates type
    if 'coords' in req_args.keys():
        if req_args.get('coords').lower() in spec.get('geog'):
            options.update(coords=req_args.get('coords'))
        else:
            msg = 'Allowable coordinates: {0:s}'.format(str(spec.get('geog')))
            raise ValueError(400, msg)
    else:
        if config.get('default', 'coordinates') in spec.get('geog'):
            options.update(coords=config.get('default', 'coordinates'))
        else:
            msg = 'Config: coords not in {0:s}'.format(str(spec.get('geog')))
            raise ValueError(500, msg)

    # Subtaxa inclusion in the query
    choice = req_args.get('includelower',
                          str(config.get('default', 'includelower')))
    options.update(includelower=literal_eval(choice.capitalize()))

    # Limit records in the query
    choice = req_args.get('limit',
                          int(config.get('default', 'limit')))
    options.update(limit=int(choice))

    return options


def id_parse(ids, db, endpoint):
    """
    Separate [database]:[datatype]:[id_number] from a list.

    :arg ids: array of database specific object identifiers in above format
    :type ids: list (of str)
    :arg db: database name to parse on
    :type db: str
    :arg endpoint: endpoint to parse on
    :type endpoint: str

    """
    import re

    numeric_ids = list()
    db_tag = db[:4]

    # Add additional db specific locale eqivalents here
    loc_spec = ['col', 'dst']

    for id in ids:
        database = re.search('^\w+(?=:)', id).group()
        datatype = re.search('(?<=:).+(?=:)', id).group()
        id_num = int(re.search('\d+$', id).group())

        if endpoint == 'loc':
            if database.lower() == db_tag and datatype.lower() in loc_spec:
                numeric_ids.append(id_num)
        elif endpoint not in loc_spec:
            if database.lower() == db_tag and datatype.lower() == endpoint:
                numeric_ids.append(id_num)

    return numeric_ids


def parse(req_args, options, db, endpoint):
    """Return a Requests payload specific to resource target."""
    from ..elc import config, aux

    # Alowable endpoint parameters (add specification for additional below)

    spec = dict()
    spec.update(occ=['bbox', 'agerange', 'ageunits', 'timerule', 'taxon',
                     'includelower', 'limit', 'offset', 'show', 'output'])
    spec.update(loc=['occid', 'bbox', 'agerange', 'ageunits', 'timerule',
                     'taxon', 'includelower', 'limit', 'offset', 'show'])
    spec.update(tax=['taxon', 'includelower', 'hierarchy'])
    spec.update(ref=['idnumbers', 'format'])
    spec.update(timebound=['agerange', 'ageunits'])
    spec.update(paleocoords=['coords', 'age', 'ageunits'])

    # Bad or missing parameter checks

    if not bool(req_args):
        msg = 'No parameters provided.'
        raise ValueError(400, msg)

    for param in req_args.keys():
        if param not in spec.get(endpoint):
            msg = 'Unknown parameter: {0:s}'.format(param)
            raise ValueError(400, msg)

    if db not in config.db_list():
        msg = 'Database support lacking: {0:s}'.format(db)
        raise ValueError(501, msg)

    # Generate sub-query api payload

    payload = dict()

    payload.update(aux.set_db_special(db))

    payload.update(limit=options.get('limit'))

    if 'taxon' in req_args.keys():
        try:
            payload.update(aux.set_taxon(taxon=req_args.get('taxon'),
                                         subtax=options.get('subtax'),
                                         db=db))
        except ValueError as err:
            raise ValueError(err.args[0], err.args[1])

    if 'agerange' in req_args.keys():
        try:
            payload.update(aux.set_age(age_range=req_args.get('agerange'),
                                       options=options,
                                       db=db))
        except ValueError as err:
            raise ValueError(err.args[0], err.args[1])

    if 'offset' in req_args.keys():
        if (req_args.get('offset').isalpha() or
                bool(req_args.get('offset')[0] == '-')):
            msg = 'Parameter must be a number: offset'
            raise ValueError(400, msg)
        else:
            payload.update(offset=req_args.get('offset'))

    return payload
