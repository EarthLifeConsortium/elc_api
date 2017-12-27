"""Common parameter parsing functions for the API controllers."""

import geojson
import ast
from elc import config
import pdb


def parse(req_args, db):
    """Return a Requests payload specific to resource target."""
    db_implemented = ['pbdb', 'neotoma']
    spec = ['bbox', 'minage', 'maxage', 'agescale', 'timerule',
            'taxon', 'includelower', 'limit', 'offset', 'show',
            'output']

    payload = dict()

    # Bad or missing parameter checks

    if not bool(req_args):
        msg = 'No parameters provided.'
        raise ValueError(400, msg)

    for param in req_args.keys():
        if param not in spec:
            msg = 'Unknown parameter \'{0:s}\''.format(param)
            raise ValueError(400, msg)

    if db not in db_implemented:
        msg = 'Database support lacking: \'{0:s}\''.format(db)
        raise ValueError(501, msg)

    # Set defaults

    if 'includelower' in req_args:
        inc_sub_taxa = ast.literal_eval(req_args.get('includelower'))
    else:
        inc_sub_taxa = config.get('default', 'includelower')

    if 'agescale' in req_args:
        age_units = req_args.get('agescale')
    else:
        age_units = config.get('default', 'agescale')

    # Generate sub-query api payload

    for param in req_args.keys():

        if param == 'taxon':
            if db == 'neotoma':
                if inc_sub_taxa:
                    wildcard = '{0:s}%'.format(req_args[param])
                    payload.update(taxonname=wildcard)
                else:
                    payload.update(taxonname=req_args[param])
            elif db == 'pbdb':
                if inc_sub_taxa:
                    payload.update(base_name=req_args[param])
                else:
                    payload.update(taxon_name=req_args[param])

        if param == 'limit':
            payload.update(limit=req_args[param])

        if param == 'offset':
            payload.update(offset=req_args[param])

    return payload
