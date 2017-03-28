import connexion
from swagger_server.models.error_model import ErrorModel
from swagger_server.models.site import Site
from datetime import date, datetime
from typing import List, Dict
from six import iteritems
from ..util import deserialize_date, deserialize_datetime


def site(occid=None, bbox=None, minage=None, maxage=None, agescale=None, timerule=None, taxon=None, includelower=None):
    """
    Sample sites or localities
    Return sampling locations in space and time, excluding occurrence records. This may return multiple stes from a common spatial location if the samples from the synthetic sites represent unique collections. This terminology is similar to the the datasets concept in Neotoma
    :param occid: Unique numeric ID, or vector of IDs for occurrences
    :type occid: int
    :param bbox: Bounding box definition, either as a numeric vector of form [lonW, latS, lonE, latN] or as structured WKT text
    :type bbox: str
    :param minage: The most recent age for the temporal search window. By default the minage is  present, or not used in queries. Units are millions of years ago, unless defined using agescale
    :type minage: float
    :param maxage: The oldest age for the temporal search window. Units are millions of years ago, unless defined using agescale
    :type maxage: float
    :param agescale: The units for maxage and minage. Allowable units are yr, ka or ma
    :type agescale: str
    :param timerule: Control the application of the temporal bounding box. May choose one of three rules, contain, all samples must be fully within the temporal bounding box; major, more than half of an occurrences temporal uncertainty must be within the bounding box; overlap, any portion of an occurrence may be withing the bounding box
    :type timerule: str
    :param taxon: Taxonomic name. May be truncated, a list of taxa or use wildcards. If a specific taxon ID or a vector of IDs is known that parameter can be passed through taxon. Taxon lists must be passed using JSON formating. By default, returns only taxa named in the query. Use includelower if all lower taxa are desired
    :type taxon: str
    :param includelower: A boolean, if TRUE, all species and subspecies lower taxa of a named genera will be included in the response
    :type includelower: bool

    :rtype: List[Site]
    """
    return 'do some magic!'
