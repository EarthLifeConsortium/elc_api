"""Auxilary functions for the API controllers."""

def get_subtaxa(taxon, syn=True):
    """
    Query PBDB for all lower order relatives of a specified taxa.
    
    :arg taxon: Taxonmic name to query
    :arg syn: Boolean, include recognized synonyms in the return
    """
