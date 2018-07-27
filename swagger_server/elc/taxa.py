"""Functions related to taxa formatting and hierarchy."""


def set_taxon(taxon, subtax, db):
    """Return a database specific key-val pair for taxon."""
    import requests

    # Parse incomming taxon name string for errors and reassemble
    taxon_list = taxon.split(',')
    taxon_list = [x.strip() for x in taxon_list]
    taxon_list = [x.capitalize() for x in taxon_list]

    clean_list = list()
    for item in taxon_list:

        if len(item.split()) > 3 or len(item.split()) == 0:
            msg = 'Unsupported taxon name length: {0:s}'.format(item)
            raise ValueError(400, msg)

        # Remove "not" portion of logical qualifier if unsupported by DB
        if '^' in item and db != 'pbdb':
            clean_list.append(item[:item.find('^')])
        else:
            clean_list.append(item)

    taxon = ','.join(clean_list)

    # Format for specific database API parameter payloads
    if db == 'neotoma':
        if subtax:
            return {'taxonname': taxon,
                    'lower': 'true'}
        else:
            return {'taxonname': taxon}

    elif db == 'pbdb':
        if subtax:
            return {'base_name': taxon}
        else:
            return {'taxon_name': taxon}

    elif db == 'sead':
        # Currently SEAD does not support general taxa serching.
        # An external service must be used to resolve the taxon rank of
        # the first name in a list of taxa prior to parameterizing the query

        single_taxon = taxon.split(',')[0]

        if len(single_taxon.split()) == 2:
            # Consider this to be a 'Genus Species' name
            query = 'ilike.*{0:s}'.format(single_taxon)
            return {'taxon': query}
        else:
            url = 'https://paleobiodb.org/data1.2/taxa/single.json'
            payload = {'taxon_name': single_taxon}
            rank = requests.get(url, payload).json()['records'][0]['rnk']

            if rank == 9:
                # Rank of Family
                query = 'ilike.{0:s}'.format(single_taxon)
                return {'family_name': query}

            elif rank == 5:
                # Rank of Genus
                query = 'ilike.{0:s}'.format(single_taxon)
                return {'genus_name': query}

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
