"""Functions related to taxa formatting and hierarchy."""


def set_taxon(taxon, subtax, db):
    """Return a database specific key-val pair for taxon."""
    import requests

    taxon = taxon.replace(', ',',')
    taxon = taxon.split(',')
    taxon = [x.strip() for x in taxon]
    taxon = [x.capitalize() for x in taxon]
    taxon = ','.join(taxon)

    if len(taxon.split()) == 2:
        genus_species = True
    elif len(taxon.split()) == 1:
        genus_species = False
    else:
        msg = 'Taxon argument contains too many parameters'
        raise ValueError(400, msg)

    if db == 'neotoma':
        if subtax:
            return {'taxonname': taxon,
                    'lower': 'true'}
        else:
            return {'taxonname': taxon}

    elif db == 'pbdb':
        if subtax and not genus_species:
            return {'base_name': taxon}
        else:
            return {'taxon_name': taxon}

    elif db == 'sead':
        if genus_species:
            #  name = 'ilike.*{0:s}'.format(taxon.split(' ')[1])
            name = 'ilike.*{0:s}'.format(taxon)
            return {'taxon': name}
        else:
            url = 'https://paleobiodb.org/data1.2/taxa/single.json'
            payload = {'taxon_name': taxon}
            rank = requests.get(url, payload).json()['records'][0]['rnk']

            if rank == 9:
                name = 'ilike.{0:s}'.format(taxon)
                return {'family_name': name}

            elif rank == 5:
                name ='ilike.{0:s}'.format(taxon)
                return {'genus_name': name}


    # NEW RESOURCE:  Add another databse specific taxon name mapping here

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
    from ..elc import config

    subtaxa = set()
    url = ''.join([config.get('resource_api', 'pbdb'), 'taxa/list.json'])
    payload = {'rel': 'all_children', 'name': taxon}

    try:
        r = requests.get(url=url,
                         params=payload,
                         timeout=config.get('default', 'timeout'))
        r.raise_for_status()

    except requests.exceptions.HTTPError as e:
        msg = r.json().get('warnings')
        raise ValueError(r.status_code, msg)

    data = r.json()

    for rec in data['records']:
        if rec.get('tdf') and not inc_syn:
            subtaxa.add(rec.get('acn'))
        else:
            subtaxa.add(rec.get('nam'))

    return list(subtaxa)


def get_parents(taxon):
    """
    Query PBDB for parent taxonomic groups.

    :arg taxon: Taxonomic name to query
    :type taxon: str

    """
    import requests
    from collections import OrderedDict
    from ..elc import config

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
