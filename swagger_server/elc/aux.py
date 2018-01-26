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


def set_taxon(db, taxon, inc_sub_taxa):
    """
    Return a database specific key-val pair for taxon paramaterization.

    :arg db: Database name
    :type db: str
    :arg taxon: User input taxon name
    :type taxon: str
    :arg inc_sub_taxa: Include lower taxonomy switch
    :type inc_sub_taxa: bool

    :rtype: Dict[n=1]
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
        if inc_sub_taxa and not genus_species:
            wildcard = '{0:s}%'.format(taxon)
            return {'taxonname': wildcard}
        else:
            return {'taxonname': taxon}
    elif db == 'pbdb':
        if inc_sub_taxa and not genus_species:
            return {'base_name': taxon}
        else:
            return {'taxon_name': taxon}
    # Add another databse specific case here
    else:
        return {}


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


def build_meta(options):
    """Generate metadata for the composite return."""
    from ..elc import config, aux

    return {'license': config.get('default', 'license'),
            'retrieval_timestamp': aux.set_timestamp(),
            'link': 'http://earthlifeconsortium.org',
            'age_units': options.get('ageunits'),
            'coordinates': options.get('coords')}


def build_meta_sub(data, url, t0, db):
    """Generate database specific metadata object for the return."""
    from time import time
    from ..elc import config

    db_rec_name = config.get('db_rec_obj', db)

    return {db: {'subquery': url,
                 'response_time': round(time()-t0, 3),
                 'record_count': len(data.get(db_rec_name))}}


def set_age_scaler(options, db):
    """Return a numerica scale factor for ages."""
    from ..elc import config

    unit = {'yr': 1, 'ka': 1000, 'ma': 1000000}

    elc_age = unit.get(options.get('ageunits'))
    db_age = unit.get(config.get('native_ageunits', db))

    return elc_age / db_age
