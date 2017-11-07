"""Auxilary functions for the API controllers."""


def get_subtaxa(taxon, inc_syn=True):
    """
    Query PBDB for all lower order relatives of a specified taxa.

    :arg taxon: Taxonmic name to query
    :arg inc_syn: Boolean, include recognized synonyms in the return
    """
    import requests

    subtaxa = set()
    base_url = 'http://localhost/data1.2/taxa/list.json'

    payload = dict()
    payload.update(rel='all_children', name=taxon)

    resp = requests.get(base_url, params=payload, timeout=None)
    resp_json = resp.json()

    if resp.status_code == 200 and 'records' in resp_json:
        for rec in resp_json['records']:

            if rec.get('tdf') and not inc_syn:
                subtaxa.add(rec.get('acn'))
            else:
                subtaxa.add(rec.get('nam'))

        return subtaxa
