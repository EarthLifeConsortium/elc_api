import connexion
from swagger_server.models.error_model import ErrorModel
from swagger_server.models.taxonomy import Taxonomy
from datetime import date, datetime
from typing import List, Dict
from six import iteritems
from ..util import deserialize_date, deserialize_datetime


def taxon(taxon=None, includelower=None, hierarchy=None):
    """
    Taxonomic information, or hierarchy
    Returns detailed taxonomic information for the given query. Queries may include partial matches, and may request lower taxa using the boolean includelower parameter. In cases where hierarchy is also requested the user may set hierarchy to TRUE
    :param taxon: Taxonomic name. May be truncated, a list of taxa or use wildcards. If a specific taxon ID or a vector of IDs is known that parameter can be passed through taxon. Taxon lists must be passed using JSON formating. By default, returns only taxa named in the query. If all lower taxa are desired in the return, use includelower
    :type taxon: str
    :param includelower: If TRUE, all species and subspecies of a named genera will be included in the response
    :type includelower: bool
    :param hierarchy: If TRUE, the full hierarchy for the taxon will be included in the response, otherwise just the unique entry for a match
    :type hierarchy: bool

    :rtype: List[Taxonomy]
    """
    return 'do some magic!'
