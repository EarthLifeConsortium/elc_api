"""Common parameter parsing functions for the API controllers."""


def set_options(req_args, endpoint):
    """Return a dictionary with runtime options and config."""
    from ..elc import config
    from ast import literal_eval

    # NEW RESOURCE: Optional. Add aditional formats and controls below
    # The default parameter is always taken to be param[0]
    spec = dict()
    spec.update(misc=['json'])
    spec.update(occ=['json', 'csv'])
    spec.update(loc=['json', 'csv'])
    spec.update(tax=['json', 'itis', 'csv'])
    spec.update(ref=['bibjson', 'json', 'csv', 'ris'])
    spec.update(show=['all', 'poll', 'idx'])
    spec.update(age=['ma', 'ka', 'ybp'])
    spec.update(geog=['paleo', 'modern'])

    # Runtime options
    options = dict()

    # Response format
    if 'output' in req_args.keys():
        if req_args.get('output').lower() in spec.get(endpoint):
            options.update(output=req_args.get('output').lower())
        else:
            msg = 'Allowable formats: {0:s}'.format(str(spec.get(endpoint)))
            raise ValueError(400, msg)
    else:
        options.update(output=spec.get(endpoint)[0])

    # Response includes
    if 'show' in req_args.keys():
        if req_args.get('show').lower() in spec.get('show'):
            options.update(show=req_args.get('show').lower())
        else:
            msg = 'Allowable show args: {0:s}'.format(str(spec.get('show')))
            raise ValueError(400, msg)
    else:
        options.update(show=spec.get('show')[0])

    # Age measurement units
    if 'ageunits' in req_args.keys():
        if req_args.get('ageunits').lower() in spec.get('age'):
            options.update(ageunits=req_args.get('ageunits').lower())
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
    if 'coordtype' in req_args.keys():
        if req_args.get('coordinates').lower() in spec.get('geog'):
            options.update(geog=req_args.get('coordinates').lower())
        else:
            msg = 'Allowable coordinates: {0:s}'.format(str(spec.get('geog')))
            raise ValueError(400, msg)
    else:
        if config.get('default', 'coordinates') in spec.get('geog'):
            options.update(geog=config.get('default', 'coordinates'))
        else:
            msg = 'Config: coords not in {0:s}'.format(str(spec.get('geog')))
            raise ValueError(500, msg)

    # Subtaxa inclusion in the query (override default for taxonomy route)
    if endpoint == 'tax' and 'includelower' not in req_args.keys():
        options.update(includelower=False)
    else:
        choice = req_args.get('includelower',
                              str(config.get('default', 'includelower')))
        options.update(includelower=literal_eval(choice.capitalize()))

    # Limit records in the query
    choice = req_args.get('limit',
                          int(config.get('default', 'limit')))
    options.update(limit=abs(int(choice)))

    # Mutable parameters
    options.update(tot_rec_count=0)

    return options


def id_parse(ids, db, id_type):
    """
    Separate [database]:[datatype]:[id_number] from a list.

    :arg ids: array of database specific object identifiers in above format
    :type ids: list (of str)
    :arg db: database name to parse on
    :type db: str
    :arg id_type: data type to parse on
    :type id_type: str

    """
    import re

    # NEW RESOURCE: Add additional database names and datatypes below
    spec = {'dbase': ['pbdb', 'neot'],
            'dtype': ['occ', 'sit', 'dst', 'col', 'ref', 'pub', 'txn']}

    numeric_ids = list()
    db_tag = db[:4]
    database = datatype = id_num = ''

    ids = ids.strip('"')
    id_list = [x.strip() for x in ids.split(',')]

    for id in id_list:
        try:
            database = re.search('^\w+(?=:)', id).group(0)
            database = database[:4]
            datatype = re.search('(?<=:).+(?=:)', id).group(0)
            id_num = re.search('(?:.*?:){2}(.*)', id).group(1)
        except AttributeError as err:
            msg = 'Incorrectly formatted ID: {0:s}'.format(id)
            raise ValueError(400, msg)

        if database.lower() not in spec['dbase']:
            msg = 'Unknown database: {0:s}'.format(id)
            raise ValueError(400, msg)

        if datatype.lower() not in spec['dtype']:
            msg = 'Unknown data type: {0:s}'.format(id)
            raise ValueError(400, msg)

        if not id_num.isnumeric():
            msg = 'Invalid numerical ID: {0:s}'.format(id)
            raise ValueError(400, msg)

        if database.lower() == db_tag and datatype.lower() == id_type:
            numeric_ids.append(int(id_num))

    return numeric_ids


def set_id(ids, db, endpoint, options):
    """Return a payload parameter for the requested id tag."""
    # NEW RESOURCE: Add additional database-to-datatype mappings below
    if endpoint in ['loc','ref']:
        xmap = {'pbdb': ['col', 'coll_id'],
                'neotoma': ['dst', 'datasetid']}
    #  elif endpoint == 'ref':
        #  xmap = {'pbdb': ['ref', 'ref_id'],
                #  'neotoma': ['pub', 'pubid']}
    elif endpoint == 'tax':
        xmap = {'pbdb': ['txn', 'taxon_id'],
                'neotoma': ['txn', 'taxonid']}
    else:
        return {}

    try:
        id_numbers = id_parse(ids=ids, db=db, id_type=xmap[db][0])
    except ValueError as err:
        raise ValueError(err.args[0], err.args[1])

    # Set dispacher to skip the requested DB, no IDs in the query
    if not id_numbers:
        options.update(skip=True)

    id_string = ','.join(str(x) for x in id_numbers)

    return {xmap[db][1]: id_string}


def parse(req_args, options, db, endpoint):
    """Return a Requests payload specific to resource target."""
    from ..elc import config, aux, ages, taxa, geog

    # Alowable endpoint parameters

    spec = dict()
    spec.update(occ=['bbox', 'agerange', 'ageunits', 'timerule', 'taxon',
                     'includelower', 'coordinates', 'limit', 'offset',
                     'show', 'output', 'run'])
    spec.update(loc=['idlist', 'bbox', 'agerange', 'ageunits', 'timerule',
                     'coordinates', 'limit', 'offset', 'show', 'output',
                     'run'])
    spec.update(tax=['taxon', 'idlist', 'includelower', 'hierarchy',
                     'show', 'output', 'run'])
    spec.update(ref=['idlist', 'show', 'output', 'run'])
    spec.update(timebound=['agerange', 'ageunits'])
    spec.update(paleocoords=['coords', 'age', 'ageunits'])
    spec.update(subtaxa=['taxon', 'synonyms'])

    # Bad or missing parameter checks

    if not bool(req_args):
        msg = 'No parameters provided: {0:s}'.format(str(spec.get(endpoint)))
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

    if 'taxon' in req_args.keys():

        try:
            payload = taxa.set_taxon(taxon=req_args.get('taxon'),
                                     subtax=options.get('includelower'),
                                     db=db)
        except ValueError as err:
            raise ValueError(err.args[0], err.args[1])

    payload.update(aux.set_db_special(db, endpoint))

    payload.update(limit=options.get('limit'))

    if 'idlist' in req_args.keys():

        try:
            payload.update(set_id(ids=req_args.get('idlist'),
                                  db=db,
                                  endpoint=endpoint,
                                  options=options))

        except ValueError as err:
            raise ValueError(err.args[0], err.args[1])

    if 'agerange' in req_args.keys():

        try:
            payload.update(ages.set_age(age_range=req_args.get('agerange'),
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

    if 'bbox' in req_args.keys():

        try:
            payload.update(geog.set_location(wkt=req_args.get('bbox'), db=db))
        except ValueError as err:
            raise ValueError(err.args[0], err.args[1])

    return payload
