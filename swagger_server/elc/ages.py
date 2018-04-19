"""Functions related to geologic ages, time bounds and time conversions."""


def set_age_scaler(options, db):
    """Return a numerical scale factor for ages."""
    from ..elc import config

    unit = {'yr': 1, 'ka': 1000, 'ma': 1000000}

    elc_age = unit.get(options.get('ageunits'))
    db_age = unit.get(config.get('native_ageunits', db))

    return elc_age / db_age


def set_age(age_range, options, db):
    """Return key-val ages for identified database subquery payload."""
    from ..elc import ages

    try:
        early_age, late_age, \
            col_hex, age_ref = ages.get_age(age_range=age_range,
                                            options=options)
    except ValueError as err:
        raise ValueError(err.args[0], err.args[1])

    factor = ages.set_age_scaler(options, db)

    if db == 'neotoma':
        return {'ageolder': round((early_age * factor), 4),
                'ageyounger': round((late_age * factor), 4)}
    elif db == 'pbdb':
        return {'max_ma': round((early_age * factor), 4),
                'min_ma': round((late_age * factor), 4)}
    # Add another databse specific case here
    else:
        return {}


def get_age(age_range, options):
    """Parse age range parameters."""
    from ..elc import ages

    col_hex = None
    age_ref = None

    bound = list()
    for val in age_range.split(','):
        bound.append(val.strip())

    if '' in bound:
        msg = 'Incorrectly formatted parameter pair: agerange'
        raise ValueError(400, msg)

    # Sub-service requires ageunits as 'ma'
    factor = ages.set_age_scaler(options, 'pbdb')

    if len(bound) == 1:

        if bound[0].isalpha():
            ea1, la1 = [x / factor for x in ages.resolve_age(bound[0])]
            col_hex, age_ref = ages.get_age_meta(bound[0])
        elif float(bound[0]) < 0:
            msg = 'Parameter out of bounds: agerange'
            raise ValueError(400, msg)
        else:
            msg = 'Incorrect number of parameters: agerange'
            raise ValueError(400, msg)

        return round(ea1, 2), round(la1, 2), col_hex, age_ref

    if len(bound) == 2:

        if bound[0].isalpha():
            ea1, la1 = [x / factor for x in ages.resolve_age(bound[0])]
            if not col_hex:
                col_hex, age_ref = ages.get_age_meta(bound[0])
        elif float(bound[0]) < 0:
            msg = 'Parameter out of bounds: agerange'
            raise ValueError(400, msg)
        else:
            ea1 = la1 = float(bound[0])

        if bound[1].isalpha():
            try:
                ea2, la2 = [x / factor for x in ages.resolve_age(bound[1])]
            except ValueError as err:
                raise ValueError(err.args[0], err.args[1])
            if not col_hex:
                col_hex, age_ref = ages.get_age_meta(bound[1])
        elif float(bound[1]) < 0:
            msg = 'Parameter out of bounds: agerange'
            raise ValueError(400, msg)
        else:
            ea2 = la2 = float(bound[1])

        if ea1 < ea2:
            ea1, ea2, la1, la2 = ea2, ea1, la2, la1

        return round(ea1, 2), round(la2, 2), col_hex, age_ref

    else:
        msg = 'Incorrect number of parameters: agerange'
        raise ValueError(400, msg)


def resolve_age(geologic_age):
    """Query PBDB for find early and late bounds for a geologic age."""
    import requests
    from ..elc import config

    url = ''.join([config.get('resource_api', 'pbdb'),
                   'intervals/single.json'])
    payload = {'name': geologic_age}

    try:
        r = requests.get(url=url,
                         params=payload,
                         timeout=config.get('default', 'timeout'))
        r.raise_for_status()

    except requests.exceptions.HTTPError as e:
        msg = '{0:s}: {1:s}'.format(r.json().get('errors')[0], geologic_age)
        raise ValueError(r.status_code, msg)

    data = r.json().get('records')[0]

    return data.get('eag'), data.get('lag')


def get_age_meta(geologic_age):
    """Retrieve ancillary data for geologic ages."""
    import requests
    from ..elc import config

    # Retrieve the color hex and timescale reference number

    url = ''.join([config.get('resource_api', 'pbdb'),
                   'intervals/single.json'])
    payload = {'name': geologic_age,
               'extids': False}

    try:
        r = requests.get(url=url,
                         params=payload,
                         timeout=config.get('default', 'timeout'))
        r.raise_for_status()

    except requests.exceptions.HTTPError as e:
        msg = '{0:s}: {1:s}'.format(r.json().get('errors')[0], geologic_age)
        raise ValueError(r.status_code, msg)

    data = r.json().get('records')[0]

    # Retrieve the bibliographic reference using the id number

    url = 'http://localhost/data1.2/refs/single.json'
    payload = {'show': 'both',
               'id': data.get('rid')[0]}

    try:
        r = requests.get(url=url,
                         params=payload,
                         timeout=config.get('default', 'timeout'))
        r.raise_for_status()

    except requests.exceptions.HTTPError as e:
        msg = r.json().get('errors')[0]
        raise ValueError(r.status_code, msg)

    ref_data = r.json().get('records')[0]

    return data.get('col'), ref_data.get('ref')
