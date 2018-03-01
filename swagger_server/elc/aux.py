"""Auxilary functions for the API controllers."""


def set_timestamp():
    """Format POSIX UTC time for metadata."""
    from time import gmtime

    t = gmtime()
    return '{0:4d}-{1:02d}-{2:02d} {3:02d}:{4:02d}:{5:02d} UTC'.format(
        t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)


def set_db_special(db):
    """Add custom payload additions unique to a specific db."""
    if db == 'pbdb':
        return {'show': 'full'}
    # Add another database specific case here
    else:
        return {}


def set_taxon(taxon, subtax, db):
    """
    Return a database specific key-val pair for taxon paramaterization.

    :arg db: database name
    :type db: str
    :arg taxon: user input taxon name
    :type taxon: str
    :arg subtax: include lower taxonomy switch
    :type subtax: bool

    """
    taxon = taxon.capitalize()

    if len(taxon.split()) == 2:
        genus_species = True
    elif len(taxon.split()) == 1:
        genus_species = False
    else:
        msg = 'Taxon argument contains too many parameters'
        raise ValueError(400, msg)

    if db == 'neotoma':
        if subtax and not genus_species:
            wildcard = '{0:s}%'.format(taxon)
            return {'taxonname': wildcard}
        else:
            return {'taxonname': taxon}
    elif db == 'pbdb':
        if subtax and not genus_species:
            return {'base_name': taxon}
        else:
            return {'taxon_name': taxon}
    # Add another databse specific case here
    else:
        return {}


def set_age(age_range, options, db):
    """Return key-val ages for identified database subquery payload."""
    from ..elc import aux

    try:
        early_age, late_age = aux.get_age(age_range=age_range,
                                          options=options)
    except ValueError as err:
        raise ValueError(err.args[0], err.args[1])

    factor = aux.set_age_scaler(options, db)

    if db == 'neotoma':
        return {'ageyounger': early_age * factor,
                'ageolder': late_age * factor}
    elif db == 'pbdb':
        return {'max_ma': early_age * factor,
                'min_ma': late_age * factor}
    # Add another databse specific case here
    else:
        return {}


def get_age(age_range, options):
    """
    Parse age range parameters.

    :arg age_range: one or two comma separated numerical or text geoage bounds
    :type age_range: str
    :arg age_units: dimension of age parameter
    :type age_units: str ['yr', 'ka' or 'ma']

    """
    from ..elc import aux

    bound = age_range.split(',')
    if '' in bound:
        msg = 'Incorrectly formatted parameter pair: agerange'
        raise ValueError(400, msg)

    factor = aux.set_age_scaler(options, 'pbdb')

    if len(bound) == 1:

        if bound[0].isalpha():
            ea1, la1 = [x / factor for x in aux.resolve_age(bound[0])]
        elif float(bound[0]) < 0:
            msg = 'Parameter out of bounds: agerange'
            raise ValueError(400, msg)
        else:
            msg = 'Incorrect number of parameters: agerange'
            raise ValueError(400, msg)

        return round(ea1, 2), round(la1, 2)

    if len(bound) == 2:

        if bound[0].isalpha():
            ea1, la1 = [x / factor for x in aux.resolve_age(bound[0])]
        elif float(bound[0]) < 0:
            msg = 'Parameter out of bounds: agerange'
            raise ValueError(400, msg)
        else:
            ea1 = la1 = float(bound[0])

        if bound[1].isalpha():
            ea2, la2 = [x / factor for x in aux.resolve_age(bound[1])]
        elif float(bound[1]) < 0:
            msg = 'Parameter out of bounds: agerange'
            raise ValueError(400, msg)
        else:
            ea2 = la2 = float(bound[1])

        if ea1 < ea2:
            ea1, ea2, la1, la2 = ea2, ea1, la2, la1

        return round(ea1, 2), round(la2, 2)

    else:
        msg = 'Incorrect number of parameters: agerange'
        raise ValueError(400, msg)


def resolve_age(geologic_age):
    """Query PBDB for find early and late bounds for a geologic age."""
    import requests

    url = 'https://paleobiodb.org/data1.2/intervals/single.json'
    payload = {'name': geologic_age}

    try:
        r = requests.get(url, payload)
        r.raise_for_status()

    except requests.exceptions.HTTPError as e:
        msg = '{0:s}: {1:s}'.format(r.json().get('errors')[0], geologic_age)
        raise ValueError(r.status_code, msg)

    data = r.json().get('records')[0]

    return data.get('eag'), data.get('lag')


def get_subtaxa(taxon, inc_syn=True):
    """
    Query PBDB for all lower order relatives of a specified taxa.

    :arg taxon: Taxonmic name to query
    :type taxon: str
    :arg inc_syn: Include recognized synonyms in the return
    :type inc_syn: bool

    """
    import requests
    from .elc import config

    subtaxa = set()
    base_url = config.get('resource_api', 'pbdb') + 'taxa/list.json'

    payload = dict()
    payload.update(rel='all_children', name=taxon)

    resp = requests.get(base_url, params=payload, timeout=None)

    if resp.status_code == 200:
        resp_json = resp.json()

        if 'warnings' in resp_json:
            raise ValueError(400, str(resp_json['warnings'][0]))

        else:
            for rec in resp_json['records']:
                if rec.get('tdf') and not inc_syn:
                    subtaxa.add(rec.get('acn'))
                else:
                    subtaxa.add(rec.get('nam'))
            return subtaxa

    else:
        raise ValueError(resp.status_code, resp.reason)


def get_parents(taxon):
    """
    Query PBDB for parent taxonomic groups.

    :arg taxon: Taxonomic name to query
    :type taxon: str

    """
    import requests
    from collections import OrderedDict
    from .elc import config

    parents = dict()
    base_url = config.get('resource_api', 'pbdb') + 'taxa/list.json'
    tax_sys = ['kingdom', 'phylum', 'class', 'order',
               'family', 'genus', 'species']

    payload = dict()
    payload.update(vocab='pbdb', rel='all_parents',
                   order='hierarchy', name=taxon)

    resp = requests.get(base_url, params=payload, timeout=None)

    if resp.status_code == 200:
        resp_json = resp.json()

        if 'warnings' in resp_json:
            raise ValueError(400, 'Bad Request',
                             str(resp_json['warnings'][0]))

        else:
            for rec in resp_json['records']:
                for rank in tax_sys:
                    if rec.get('taxon_rank') == rank:
                        parents.update({rank: rec.get('taxon_name')})
            return OrderedDict(parents)

    else:
        raise ValueError(resp.status_code, resp.reason,
                         'Server error or bad URL')


def get_id_numbers(data, endpoint):
    """Return a list of the specified endpoint's primary id numbers."""
    ids = list()
    id_field = '{0:s}_id'.format(endpoint)

    for rec in data:
        ids.append(rec.get(id_field))

    return ids


def build_meta(ageunits=None, coords=None):
    """Generate metadata for the composite return."""
    from ..elc import config, aux

    return {'license': config.get('default', 'license'),
            'retrieval_timestamp': aux.set_timestamp(),
            'source': 'http://earthlifeconsortium.org',
            'age_units': ageunits,
            'coordinates': coords}


def build_meta_sub(source, t0, sub_tag, data=None):
    """Generate database specific metadata object for the return."""
    from time import time
    from ..elc import config

    if data:
        rec_cnt = len(data.get(config.get('db_rec_obj', sub_tag)))
    else:
        rec_cnt = 1

    return {sub_tag: {'subquery': source,
                      'response_time': round(time()-t0, 3),
                      'record_count': rec_cnt}}


def set_age_scaler(options, db):
    """Return a numerical scale factor for ages."""
    from ..elc import config

    unit = {'yr': 1, 'ka': 1000, 'ma': 1000000}

    elc_age = unit.get(options.get('ageunits'))
    db_age = unit.get(config.get('native_ageunits', db))

    return elc_age / db_age
