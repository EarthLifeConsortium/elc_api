"""
RESTful API controller.

Endpoint for queries on geolocated locales.
Dataset identifiers are returned for Neotoma and collection identifiers
for the PBDB.
"""

import pdb
import requests
import time
import connexion
from flask import request, jsonify
from statistics import mean
from ..elc import params


def loc(occid=None, bbox=None, minage=None, maxage=None, ageunits=None,
        timerule=None, taxon=None, includelower=None, limit=None,
        offset=None, show=None):
    """
    Return locale identifiers from Neotoma and PBDB.

    A locale in PBDB is a collection, in Neotoma it is every individual
    dataset in a site.

    :arg show=idx:  return indicies list as a json object (possibly a long string)
    :arg show=poll: return only the description object
    """
    # Parameter checks
    if not bool(request.args):
        return connexion.problem(status=400,
                                 title='Bad Request',
                                 detail='No parameters provided.',
                                 type='about:blank')
    if occid and taxon:
        return connexion.problem(status=400,
                                 title='Bad Request',
                                 detail='Specify either occurence ID or taxon, not both.',
                                 type='about:blank')

    # Init core returned objects
    desc_obj = dict()
    indicies = set()
    ret_obj = list()
    age_units = 'ma'
    full_return = False

    if show:
        show_params = show.lower().split(',')
    else:
        show_params = list()

    desc_obj.update(query={'endpoint': 'loc',
                           'occid': occid,
                           'bbox': bbox,
                           'minage': minage,
                           'maxage': maxage,
                           'ageunits': ageunits,
                           'timerule': timerule,
                           'taxon': taxon,
                           'includelower': includelower,
                           'limit': limit,
                           'offset': offset,
                           'show': show})

    #######################################
    # Query the Neotoma Database (Datasets)
    #######################################
    t0 = time.time()
    base_url = 'http://api.neotomadb.org/v1/data/datasets'
    payload = dict()
    geog_coords = 'modern'

    # Parse arguments and format database api parameters
    #  if occid:
        #  id = 
        #  payload.update(neotoma_occ_identifier=occid)

    # Set geographical constraints (can be WKT)
    if bbox:
        params.set_geography(payload, bbox, 'neot')

    # Set all age parameters to year, kilo-year or mega-annum
    if ageunits:
        age_scaler = params.set_age(payload, ageunits, minage, maxage, 'neot')

    # Set timescale bounding rules
    # Note: Timerules are not currently supported by the Neotoma API.
    #  if timerule:
        #  params.set_timebound(payload, timerule, 'neot')

    # Set specific taxon search or allow lower taxa as well,
    # default if parameter omitted is True
    #   Note: Including subtaxa is dataset searches is not currently
    #   supported by the Neotoma API. Wildcard completion is an
    #   imperfect workaround.
    if taxon:
        if includelower or includelower == None:
            subtaxa = taxon + '%'
            payload.update(taxonname=subtaxa)
        else:
            payload.update(taxonname=taxon)
    
    # Set constraints on the data return
    #   Note: Not currently supported in Neotoma API
    #  if limit:
        #  payload.update(limit=limit)
    #  else:
        #  payload.update(limit='999999')

    # Offset the returned records, used with limit for large returns
    #   Note: Not currently supported in Neotoma API
    #  if offset:
        #  payload.update(offset=offset)

    # Issue GET request to Neotoma
    #   Note: The Neotoma API does not currently support searching by
    #   occurrence so disable the request entirely if this parameter
    #   is specified. PBDB search will still work.
    if occid:
        resp = None
    else:
        resp = requests.get(base_url, params=payload, timeout=None)

    # Parse Neotoma return and add to the response object
    if resp.status_code == 200:
        resp_json = resp.json()
        if 'data' in resp_json:
            for rec in resp_json['data']:
                loc_obj = dict()
                loc_id = 'neot:dst:' + str(rec.get('DatasetID'))

                try:
                    loc_name = rec['Site']['SiteName']
                except:
                    loc_name = None

                try:
                    max_age = float(rec.get('AgeOldest')) * age_scaler
                    min_age = float(rec.get('AgeYoungest')) * age_scaler
                except:
                    max_age = None
                    min_age = None

                try:
                    lat = mean([rec['Site']['LatitudeNorth'],
                                rec['Site']['LatitudeSouth']])
                    lon = mean([rec['Site']['LongitudeEast'],
                                rec['Site']['LongitudeWest']])
                except:
                    lat = None
                    lon = None

                loc_obj.update(lat=round(lat,5),
                               lon=round(lon,5),
                               locale_name=loc_name,
                               dataset_type=rec.get('DatasetType'),
                               min_age=min_age,
                               max_age=max_age,
                               age_basis=rec.get('CollUnitType'),
                               locale_id=loc_id,
                               geog_coords=geog_coords)

                # Add the fomatted locale data to the return
                ret_obj.append(loc_obj)

                # Add the unique database ID to the returned string
                indicies.add(loc_id)

            # Build the JSON description object
            t1 = round(time.time()-t0, 3)
            desc_obj.update(neotoma={'response_time': t1,
                                     'status_codes': resp.status_code,
                                     'subqueries': resp.url,
                                     'record_count': len(resp_json['data'])})

    ###############################################
    # Query the Paleobiology Database (Collections)
    ###############################################
    t0 = time.time()
    base_url = 'http://paleobiodb.org/data1.2/colls/list.json'
    payload = dict()
    geog_coords = 'paleo'
    payload.update(vocab='pbdb', show='loc')

    # Parse arguments and format database api parameters
    if occid:
        payload.update(occ_id=occid)

    # Test if geography is lat/lon rectangle or WKT
    if bbox:
        if len(bbox) == 4:
            bbox_list = bbox.split(',')
            payload.update(lngmin=bbox_list[0], latmin=bbox_list[1],
                           lngmax=bbox_list[2], latmax=bbox_list[3])
        else:
            payload.update(loc=box)

    # Set all age parameters to year, kilo-year or mega-annum
    if ageunits and ageunits.lower() == 'yr':
        age_scaler = 1e06
        age_units = 'yr'
        if minage:
            payload.update(min_ma=float(minage)/age_scaler)
        if maxage:
            payload.update(max_ma=float(maxage)/age_scaler)
    elif ageunits and ageunits.lower() == 'ka':
        age_scaler = 1e03
        age_units = 'ka'
        if minage:
            payload.update(min_ma=float(minage)/age_scaler)
        if maxage:
            payload.update(max_ma=float(maxage)/age_scaler)
    else:
        age_scaler = 1
        age_units = 'ma'
        if minage:
            payload.update(min_ma=minage)
        if maxage:
            payload.update(max_ma=maxage)

    # Set the timescale bounding rules
    if timerule:
        payload.update(timerule=timerule)

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

    # Issue GET request to database API
    resp = requests.get(base_url, params=payload, timeout=None)

    if resp.status_code == 200:
        resp_json = resp.json()
        if 'records' in resp_json:
            for rec in resp_json['records']:
                loc_obj = dict()
                loc_id = 'pbdb:col:' + str(rec.get('collection_no'))

                if rec.get('max_ma') and rec.get('min_ma'):
                    max_age = float(rec.get('max_ma')) * age_scaler
                    min_age = float(rec.get('min_ma')) * age_scaler
                else:
                    max_age = None
                    min_age = None

                lat = float(rec.get('lat'))
                lon = float(rec.get('lng'))
 
                loc_obj.update(lat=round(lat,5),
                               lon=round(lon,5),
                               locale_name=rec.get('collection_name'),
                               dataset_type='faunal',
                               min_age=min_age,
                               max_age=max_age,
                               age_basis='stratigraphy',
                               locale_id=loc_id,
                               geog_coords=geog_coords)
                               #  occurrences=occ_list)

                # Add the fomatted locale data to the return
                ret_obj.append(loc_obj)

                # Add the unique database ID to the returned string
                indicies.add(loc_id)

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
        return jsonify(description=desc_obj, records=ret_obj)
