"""Auxilary functions for the API controllers."""


def get_subtaxa(taxon, inc_syn=True):
    """
    Query PBDB for all lower order relatives of a specified taxa.

    :arg taxon: Taxonmic name to query
    :arg inc_syn: Boolean, include recognized synonyms in the return
    """
    import requests
    from ..ControllerCommon import settings

    subtaxa = set()
    base_url = settings.config('db_api', 'pbdb') + 'taxa/list.json'

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
    """
    import requests
    from collections import OrderedDict
    from ..ControllerCommon import settings

    parents = dict()
    base_url = settings.config('db_api', 'pbdb') + 'taxa/list.json'
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
