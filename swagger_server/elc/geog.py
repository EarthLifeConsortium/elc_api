"""Functions related to geographic coordinates and paleo conversions."""


def get_geog(coords, age, options):
    """Parse paleo geography parameters."""
    from ..elc import ages

    modern = [x.strip() for x in coords.split(',')]
    if '' in modern or len(modern) != 2:
        msg = 'Second parameter not found in pair: coords'
        raise ValueError(400, msg)

    for value in modern:
        try:
            float(value)
        except ValueError as err:
            msg = 'Non-numeric in parameter pair: coords'
            raise ValueError(400, msg)

    if any(x in age for x in [',', '.']):
        msg = 'Single integer or geologic name required: age'
        raise ValueError(400, msg)

    # Sub-service requires ageunits as 'ma'
    factor = ages.set_age_scaler(options, 'pbdb')

    if age.isalpha():
        try:
            ea1, la1 = ages.resolve_age(age)
            age = round((ea1 + la1) / 2)
        except ValueError as err:
            raise ValueError(err.args[0], err.args[1])

    else:
        age = round(int(age) * factor)

    paleo, geog_ref = resolve_geog(lat=float(modern[0]),
                                   lon=float(modern[1]),
                                   mean_age=age)

    paleo = [round(x,4) for x in paleo]
    modern = [round(float(x),4) for x in modern]

    return paleo, modern, geog_ref


def resolve_geog(lat, lon, mean_age):
    """Query GPlates model (hosted by MacroStrat) for paleocoordinates."""
    import requests
    from ..elc import config

    url = 'https://macrostrat.org/gplates/reconstruct'
    payload = {'lat': lat, 'lng': lon, 'age': mean_age}

    try:
        r = requests.get(url=url,
                         params=payload,
                         timeout=config.get('default', 'timeout'))
        r.raise_for_status()

    except requests.exceptions.HTTPError as e:
        msg = '{0:s}'.format(r.json().get('error'))
        raise ValueError(r.status_code, msg)

    if r.json().get('features')[0]['geometry']:
        coords = r.json().get('features')[0]['geometry']['coordinates']
        geog_ref = r.json().get('properties')['model']['citation']
        return coords, geog_ref
    else:
        msg = 'Unavailable point or inalid WGS84 coords (-180 to 180 degrees)'
        raise ValueError(400, msg)
