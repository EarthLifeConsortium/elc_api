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


def set_taxon(db, taxon, subtax):
    """
    Return a database specific key-val pair for taxon paramaterization.

    :arg db: Database name
    :type db: str
    :arg taxon: User input taxon name
    :type taxon: str
    :arg subtax: Include lower taxonomy switch
    :type subtax: bool

    :rtype: Dict[n=1]
    """
    taxon = taxon.capitalize()

    if len(taxon.split()) == 2:
        genus_species = True
    elif len(taxon.split()) == 1:
        genus_species = False
    else:
        msg = 'Taxon argument contains too many parameters'
        raise SyntaxError(400, msg)

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


def set_age(age_range):
    """
    Parse age range parameters.

    :arg age_range: 2 comma separated numerical or text geo age bounds
    :type age_range: str

    """
    from ..elc import aux

    bound = age_range.split(',')

    if len(bound) == 1:

        if bound[0] < 0:
            msg = 'Age parameter out of bounds'
            return SyntaxError(400, msg)

        if bound[0].isalpha():
            ea1, la1 = aux.resolve_age(bound[0])
        else:
            msg = 'Incorrect number of parameters: agerange'
            return SyntaxError(400, msg)

        return ea1, la1

    if len(bound) == 2:

        if bound[0].isalpha():
            ea1, la1 = aux.resolve_age(bound[0])
        elif float(bound[0]) < 0:
            msg = 'Age parameter out of bounds'
            return SyntaxError(400, msg)
        else:
            ea1 = la1 = float(bound[0])

        if bound[1].isalpha():
            ea2, la2 = aux.resolve_age(bound[1])
        elif float(bound[1]) < 0:
            msg = 'Age parameter out of bounds'
            return SyntaxError(400, msg)
        else:
            ea2 = la2 = float(bound[1])

        if ea1 < ea2:
            ea1, ea2, la1, la2 = ea2, ea1, la2, la1

        return ea1, la2

    else:
        msg = 'Incorrect number of parameters: agerange'
        return SyntaxError(400, msg)


def resolve_age(geologic_age):
    """Query PBDB for find early and late bounds for a geologic age."""
    import requests

    url = 'https://paleobiodb.org/data1.2/intervals/single.json'
    payload = {'name': geologic_age}

    try:
        r = requests.get(url, payload)
        r.raise_for_status()

    except requests.exceptions.HTTPError as e:
        print('Status code: ' + str(r.status_code))

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
            raise SyntaxError(400, 'Bad Request',
                              str(resp_json['warnings'][0]))

        else:
            for rec in resp_json['records']:
                if rec.get('tdf') and not inc_syn:
                    subtaxa.add(rec.get('acn'))
                else:
                    subtaxa.add(rec.get('nam'))
            return subtaxa

    else:
        raise ValueError(resp.status_code, resp.reason,
                         'Server error or bad URL')


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

    db_rec_name = config.get('db_rec_obj', sub_tag)

    if data:
        rec_cnt = len(data.get(db_rec_name))
    else:
        rec_cnt = 1

    return {sub_tag: {'subquery': source,
                      'response_time': round(time()-t0, 3),
                      'record_count': rec_cnt}}


def set_age_scaler(options, db):
    """Return a numerica scale factor for ages."""
    from ..elc import config

    unit = {'yr': 1, 'ka': 1000, 'ma': 1000000}

    elc_age = unit.get(options.get('ageunits'))
    db_age = unit.get(config.get('native_ageunits', db))

    return elc_age / db_age
