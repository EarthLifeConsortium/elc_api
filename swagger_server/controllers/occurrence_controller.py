"""
RESTful API controller.

Endpoint for queries on taxonomic occurrences in time and space.
"""

import requests
import time
import connexion
from flask import request, jsonify
from statistics import mean
from .ControllerCommon import params, settings, formatters


def occ(bbox=None, minage=None, maxage=None, agescale=None, timerule=None,
        taxon=None, includelower=None, limit=None, offset=None, show=None,
        format=None):
    """
    Return occurrence identifiers from Neotoma and PBDB.

    :arg show=idx: return indicies list as a json object (possibly a long string)
    :arg show=poll: return only the description object
    """
    # Parameter checks
    if not bool(request.args):
        return connexion.problem(status=400,
                                 title='Bad Request',
                                 detail='No parameters provided.',
                                 type='about:blank')

    # Init core returned objects
    desc_obj = dict()
    indicies = set()
    occ_return = list()

    # Parse return type
    if show:
        show_params = show.lower().split(',')
    else:
        show_params = list()

    # Set default age units if not specified
    if not agescale:
        agescale = 'ma'

    # Generate query summary object
    desc_obj.update(query={'endpoint': 'occ',
                           'bbox': bbox,
                           'minage': minage,
                           'maxage': maxage,
                           'agescale': agescale,
                           'timerule': timerule,
                           'taxon': taxon,
                           'includelower': includelower,
                           'limit': limit,
                           'offset': offset,
                           'show': show,
                           'format': format})

    ##########################################
    # Query the Neotoma Database (Occurrences)
    ##########################################
    t0 = time.time()
    base_url = settings.config('db_api', 'neot') + 'occurrences'
    payload = dict()
    geog_coords = 'modern'

    # Set geographical constraints (can be WKT)
    if bbox:
        params.set_georaphy(payload, bbox, 'neot')

    # Set all age parameters to year, kilo-year or mega-annum
    age_scaler = params.set_age(payload, agescale, minage, maxage, 'neot')

    # Set timescale bounding rules
    if timerule:
        params.set_timebound(payload, timerule, 'neot')

    # Set specific taxon search or allow lower taxa as well,
    # default if parameter omitted is True
    if taxon:
        if includelower or includelower == None:
            payload.update(nametype='base', taxonname=taxon)
        else:
            payload.update(nametype='tax', taxonname=taxon)

    # Set constraints on the data return
    if limit:
        payload.update(limit=limit)
    else:
        payload.update(limit='999999')

    # Offset the returned records, used with limit for large returns
    if offset:
        payload.update(offset=offset)

    # Issue GET request to Neotoma
    resp = requests.get(base_url,
                        params=payload,
                        timeout=settings.config('timeout', 'neot'))

    # Parse Neotoma return and add to the response object
    if resp.status_code == 200:
        resp_json = resp.json()
        if 'data' in resp_json:
            for rec in resp_json['data']:
                occ = dict()

                occ_id = 'neot:occ:' + str(rec.get('OccurID'))
                taxon_id = 'neot:txn:' + str(rec.get('TaxonID'))

                if rec.get('AgeOlder') and rec.get('AgeYounger'):
                    max_age = rec.get('AgeOlder') * age_scaler
                    min_age = rec.get('AgeYounger') * age_scaler
                else:
                    max_age = None
                    min_age = None

                lat = mean([rec.get('LatitudeNorth'),
                            rec.get('LatitudeSouth')])
                lon = mean([rec.get('LongitudeEast'),
                            rec.get('LongitudeWest')])

                occ.update(occ_id=occ_id,
                           taxon=rec.get('TaxonName'),
                           taxon_id=taxon_id,
                           max_age=max_age,
                           min_age=min_age,
                           age_units=agescale,
                           lat=round(lat,5),
                           lon=round(lon,5),
                           geog_coords=geog_coords)

                # Call the appropriate output formatter
                if format and format.lower() == 'csv':
                    occ_obj = formatters.type_csv(occ)
                else:
                    occ_obj = formatters.type_json(occ)

                # Add the formatted occurrence to the return
                occ_return.append(occ_obj)

                # Add the unique database ID to the returned string
                indicies.add(occ_id)

            # Build the JSON description object
            t1 = round(time.time()-t0, 3)
            desc_obj.update(neotoma={'response_time': t1,
                                     'status_codes': resp.status_code,
                                     'subqueries': resp.url,
                                     'record_count': len(resp_json['data'])})

    ###############################################
    # Query the Paleobiology Database (Occurrences)
    ###############################################
    t0 = time.time()
    base_url = settings.config('db_api', 'pbdb') + 'occs/list.json'
    payload = dict()
    geog_coords = 'paleo'
    payload.update(show='loc,coords,coll')
    payload.update(vocab='pbdb')

    # Test if geography is lat/lon rectangle or WKT
    if bbox:
        params.set_georaphy(payload, bbox, 'pbdb')

    # Set all age parameters to year, kilo-year or mega-annum
    age_scaler = params.set_age(payload, agescale, minage, maxage, 'pbdb')

    # Set the timescale bounding rules
    if timerule:
        params.set_timebound(payload, timerule, 'pbdb')

    # Set specific taxon search or allow lower taxa as well,
    # default if parameter omitted is True
    if taxon:
        if includelower or includelower == None:
            payload.update(base_name=taxon)
        else:
            payload.update(taxon_name=taxon)

    # Set constraints on the data return
    if limit:
        payload.update(limit=limit)
    else:
        payload.update(limit='999999')

    # Offset the returned records, used with limit for large returns
    if offset:
        payload.update(offset=offset)

    # Issue GET request to PBDB
    resp = requests.get(base_url,
                        params=payload,
                        timeout=settings.config('timeout', 'pbdb'))

    # Parse PBDB return and add to the response object
    if resp.status_code == 200:
        resp_json = resp.json()
        if 'records' in resp_json:
            for rec in resp_json['records']:
                occ = dict()

                occ_id = 'pbdb:occ:' + str(rec.get('occurrence_no'))
                taxon_id = 'pbdb:txn:' + str(rec.get('accepted_no'))

                if rec.get('max_ma') and rec.get('min_ma'):
                    max_age = float(rec.get('max_ma')) * age_scaler
                    min_age = float(rec.get('min_ma')) * age_scaler
                else:
                    max_age = None
                    min_age = None

                lat = float(rec.get('lat'))
                lon = float(rec.get('lng'))

                occ.update(occ_id=occ_id,
                           taxon=rec.get('accepted_name'),
                           taxon_id=taxon_id,
                           max_age=max_age,
                           min_age=min_age,
                           age_units=agescale,
                           lat=round(lat,5),
                           lon=round(lon,5),
                           geog_coords=geog_coords)

                # Call the appropriate output formatter
                if format and format.lower() == 'csv':
                    occ_obj = formatters.type_csv(occ)
                else:
                    occ_obj = formatters.type_json(occ)

                # Add the formatted occurrence to the return
                occ_return.append(occ_obj)

                # Add the unique database ID to the returned string
                indicies.add(occ_id) 

            # Build the JSON description object
            t1 = round(time.time()-t0, 3)
            desc_obj.update(pbdb={'response_time': t1,
                                  'status_codes': resp.status_code,
                                  'subqueries': resp.url,
                                  'record_count': len(resp_json['records'])})

    # Reformat set of all retured ID numbers as a string
    id_str = ','.join(indicies)

    ####################
    # Composite response
    ####################
    if 'poll' in show_params:
        return jsonify(description=desc_obj)
    elif 'idx' in show_params:
        return jsonify(indicies=id_str)
    else:
        return jsonify(description=desc_obj, records=occ_return)
