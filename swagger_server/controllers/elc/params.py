"""Common parameter parsing functions for the API controllers."""

import geojson
import ast
from ..elc import config, aux
import pdb


def parse(req_args, db, endpoint):
    """Return a Requests payload specific to resource target."""
    db_implemented = ['pbdb', 'neotoma']
    spec = dict()
    spec.update(occ=['bbox', 'minage', 'maxage', 'agescale', 'timerule',
                     'taxon', 'includelower', 'limit', 'offset', 'show',
                     'output'])
    #  spec.update(loc=['occid', 'bbox', 'minage', 'maxage', 'agescale',
                     #  'timerule', 'taxon', 'includelower', 'limit', 'offset',
                     #  'show'])
    #  spec.update(tax=['taxon', 'includelower', 'hierarchy'])
    #  spec.update(ref=['idnumbers', 'format'])

    # Bad or missing parameter checks

    if not bool(req_args):
        msg = 'No parameters provided.'
        raise ValueError(400, msg)

    for param in req_args.keys():
        if param not in spec[endpoint]:
            msg = 'Unknown parameter \'{0:s}\''.format(param)
            raise ValueError(400, msg)

    if db not in db_implemented:
        msg = 'Database support lacking: \'{0:s}\''.format(db)
        raise ValueError(501, msg)

    # Set defaults

    if 'includelower' in req_args.keys():
        inc_sub_taxa = ast.literal_eval(req_args.get('includelower'))
    else:
        inc_sub_taxa = config.get('default', 'includelower')

    if 'agescale' in req_args.keys():
        age_units = req_args.get('agescale')
    else:
        age_units = config.get('default', 'agescale')

    if 'limit' in req_args.keys():
        resp_limit = req_args.get('limit')
    else:
        resp_limit = config.get('default', 'limit')

    # Generate sub-query api payload

    payload = dict()

    payload.update(limit=resp_limit)

    if 'taxon' in req_args.keys():
        payload.update(aux.set_taxon(db=db,
                                     taxon=req_args.get('taxon'),
                                     inc_sub_taxa=inc_sub_taxa))

    if 'offset' in req_args.keys():
        payload.update(offset=req_args[param])

    return payload
