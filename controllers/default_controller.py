
def age(occId = None, siteId = None) -> str:
    return 'age basis endpoint'

def grid(ageBound = None, ageBin = None, ageUnit = None, bbox = None, spatialBin = None, varUnit = None, presence = None) -> str:
    return 'gridded assemblage endpoint'

def occ(bbox = None, minAge = None, maxAge = None, ageScale = None, timeRule = None, taxon = None, includeLower = None, limit = None, offset = None) -> str:
    return 'occurrence endpoint'

def pub(occId = None, siteId = None, format = None) -> str:
    return 'publication endpoint'

def site(occId = None, bbox = None, minAge = None, maxAge = None, ageScale = None, timeRule = None, taxon = None, includeLower = None) -> str:
    return 'site endpoint'

def taxon(taxon = None, includeLower = None, hierarchy = None) -> str:
    return 'taxonomy endpoint'
