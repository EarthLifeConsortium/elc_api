"""Functions related to geographic coordinates and paleo conversions."""

from ..handlers import sead, pbdb, neotoma
import re


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

    if age[0].isalpha():
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

    paleo = [round(x, 4) for x in paleo]
    modern = [round(float(x), 4) for x in modern]

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
        msg = 'Unavailable point or inalid WGS84 coords'
        raise ValueError(400, msg)


def set_location(loc, db):
    """Return location constraint payload parameter."""
    
    # If the location string contains only numbers, commas, and whitespace, check to see if it is
    # a valid bounding box.
    
    if re.match('^\d[-\d.,\s]+$', loc):
        
        coords = re.split('\s*,\s*', loc)
        
        if len(coords) != 4:
            raise ValueError(400, "The value of 'bbox' must be four coordinates: lonmin,latmin,lonmax,latmax")
        
        for value in coords:
            if not re.match('^ -? (?: \d+ | \d+[.]\d* | [.]\d+ ) $', value, re.X):
                raise ValueError(400, "Bad coordinate '" + str(value) + "' in 'bbox'")
        
        lonmin, latmin, lonmax, latmax = coords
        wkt_string = None
    
    # If the location string contains 'POLYGON((', assume it is a valid WKT string. Chop off
    # anything more than 3 digits after the decimal point in all coordinates, because we are
    # dealing with latitudes and longitures that are often approximate or even deliberately
    # incorrect. Any difference smaller than 1/16 minute of arc is meaningless.
    
    elif 'POLYGON((' in loc:
        wkt_string = re.sub(r'(\d[.]\d\d\d)\d+', r'\1', loc)
        lonmin = None
        lonmax = None
        latmin = None
        latmax = None
    
    else:
        raise ValueError(400, "The value of 'bbox' must be either four coordinates or 'POLYGON((...))'")
    
    # PBDB can take either a WKT or a bounding box.
    
    if db == 'pbdb':
        return pbdb.bbox_filter(wkt_string, lonmin, latmin, lonmax, latmax)
    
    # Neotoma can only take a WKT. If four coordinates are given, they must be converted
    # into WKT.
    
    elif db == 'neotoma':
        return neotoma.bbox_filter(wkt_string, lonmin, latmin, lonmax, latmax)
        
    # SEAD can only deal with bounding boxes. If we are given a polygon, we must compute the
    # bounding coordinates.
    
    elif db == 'sead':
        return sead.bbox_filter(wkt_string, lonmin, latmin, lonmax, latmax)
    
    # NEW RESOURCE: Add databse specific WKT bounding box vocabulary here

    else:
        return {}
