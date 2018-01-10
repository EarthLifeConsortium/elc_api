"""Auxilary functions for the API controllers."""


def set_db_special(db):
    """Custom payload additions unique to a specific db."""
    if db == 'pbdb':
        return {'show': 'all'}
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
    if db == 'neotoma':
        if inc_sub_taxa:
            wildcard = '{0:s}%'.format(taxon)
            return {'taxonname': wildcard}
        else:
            return {'taxonname': taxon}
    elif db == 'pbdb':
        if inc_sub_taxa:
            return {'base_name': taxon}
        else:
            return {'taxon_name': taxon}
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
    base_url = config.get('resource_api', 'pbdb') + 'taxa/list.json'

    payload = dict()
    payload.update(rel='all_children', name=taxon)

    resp = requests.get(base_url, params=payload, timeout=None)

    if resp.status_code == 200:
        resp_json = resp.json()

        if 'warnings' in resp_json:
            raise ValueError(400, 'Bad Request',
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
