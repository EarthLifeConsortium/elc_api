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


def get_id_numbers(data, endpoint):
    """Return a list of the specified endpoint's primary id numbers."""
    ids = set()
    id_field = '{0:s}_id'.format(endpoint)

    for rec in data:
        ids.add(rec.get(id_field))

    return list(ids)


def build_meta(ageunits=None, coords=None):
    """Generate metadata for the composite return."""
    from ..elc import config, aux

    return {'license': config.get('default', 'license'),
            'retrieval_timestamp': aux.set_timestamp(),
            'source': 'http://earthlifeconsortium.org',
            'age_units': ageunits,
            'coordinates': coords}


def build_meta_sub(source, t0, sub_tag, data=None):
    """Generate database specific metadata object for the return."""
    from time import time
    from ..elc import config

    import pdb; pdb.set_trace()

    if data:
        if type(data) is list:
            rec_cnt = len(data)
        else:
            rec_cnt = len(data.get(config.get('db_rec_obj', sub_tag)))
    else:
        rec_cnt = 1

    return {sub_tag: {'subquery': source,
                      'response_time': round(time()-t0, 3),
                      'record_count': rec_cnt}}
