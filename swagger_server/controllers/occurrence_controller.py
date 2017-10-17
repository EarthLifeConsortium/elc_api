"""
RESTful API controller.

Endpoint for queries on taxonomic occurrences in time and space.
"""

import requests
import time
import connexion
from flask import request, jsonify
from statistics import mean


def format_json(occ):
    """Format the occurrence data as a JSON return."""
    fmt_occ = dict()

    for key in occ:
        fmt_occ.update({key: occ[key]})

    # End subroutine: format_json
    return fmt_occ


def format_csv(occ):
    """Format the occurrence data as a tabular CSV file."""
    fmt_occ = dict()

    # End subroutine: format_csv
    return fmt_occ

                            
def occ(bbox=None, minage=None, maxage=None, agescale=None, timerule=None,
        taxon=None, includelower=None, limit=None, offset=None, show=None,
        format=None):
    """
    Return occurrence identifiers from Neotoma and PBDB.

    :show=idx:  return indicies list as a json object (possibly a long string)
    :show=poll: return only the description object
    """
    # Initialization and parameter checks
    if not bool(request.args):
        return connexion.problem(status=400,
                                 title='Bad Request',
                                 detail='No parameters provided.',
                                 type='about:blank')

    desc_obj = dict()
    indicies = set()
    occ_return = list()
    age_units = 'ma'
    geog_coords = 'modern'

    if show:
        show_params = show.lower().split(',')
    else:
        show_params = list()

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
    base_url = 'http://apidev.neotomadb.org/v1/data/occurrences'
    payload = dict()

    # Set geographical constraints (can be WKT)
    if bbox:
        payload.update(bbox=bbox)

    # Set all age parameters to year, kilo-year or mega-annum
    if agescale and agescale.lower() == 'yr':
        age_scaler = 1
        age_units = 'yr'
        if minage:
            payload.update(ageyoung=int(minage))
        if maxage:
            payload.update(ageold=int(maxage))
    elif agescale and agescale.lower() == 'ka':
        age_scaler = 1e-03
        age_units = 'ka'
        if minage:
            payload.update(ageyoung=int(minage/age_scaler))
        if maxage:
            payload.update(ageold=int(maxage/age_scaler))
    else:
        age_scaler = 1e-06
        age_units = 'ma'
        if minage:
            payload.update(ageyoung=int(minage/age_scaler))
        if maxage:
            payload.update(ageold=int(maxage/age_scaler))

    # Set timescale bounding rules
    if timerule and timerule.lower() == 'major':
        payload.update(agedocontain=0)
    elif timerule and timerule.lower() == 'overlap':
        payload.update(agedocontain=1)

    # Set specific taxon search or allow lower taxa as well,
    # default if parameter omitted is True
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
    resp = requests.get(base_url, params=payload, timeout=None)

    # Parse Neotoma return and add to the response object
    if resp.status_code == 200:
        resp_json = resp.json()
        if 'data' in resp_json:
            for rec in resp_json['data']:
                occ_id = 'neot:occ:' + str(rec.get('OccurID'))

                occ = dict()
                occ.update(occ_id=occ_id,
                           taxon=rec.get('TaxonName'))

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

                occ.update(taxon_id=taxon_id,
                           max_age=max_age,
                           min_age=min_age,
                           age_units=age_units,
                           lat=lat,
                           lon=lon,
                           geog_coords=geog_coords)

                # Call the appropriate output formatter
                if format and format.lower() == 'csv':
                    occ_obj = format_csv(occ)
                else:
                    occ_obj = format_json(occ)

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
    base_url = 'http://paleobiodb.org/data1.2/occs/list.json'
    payload = dict()
    payload.update(show='loc,coords,coll')
    payload.update(vocab='pbdb')

    # Test if geography is lat/lon rectangle or WKT
    if bbox:
        if len(bbox) == 4:
            bbox_list = bbox.split(',')
            payload.update(lngmin=bbox_list[0], latmin=bbox_list[1],
                           lngmax=bbox_list[2], latmax=bbox_list[3])
        else:
            payload.update(loc=box)

    # Set all age parameters to year, kilo-year or mega-annum
    if agescale and agescale.lower() == 'yr':
        age_scaler = 1e06
        age_units = 'yr'
        if minage:
            payload.update(min_ma=float(minage)/age_scaler)
        if maxage:
            payload.update(max_ma=float(maxage)/age_scaler)
    elif agescale and agescale.lower() == 'ka':
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
    resp = requests.get(base_url, params=payload, timeout=None)

    # Parse PBDB return and add to the response object
    if resp.status_code == 200:
        resp_json = resp.json()
        if 'records' in resp_json:
            for rec in resp_json['records']:
                occ = dict()
                occ_id = 'pbdb:occ:' + str(rec.get('occurrence_no'))
                occ.update(occ_id=occ_id,
                           taxon=rec.get('accepted_name'))

                taxon_id = 'pbdb:txn:' + str(rec.get('accepted_no'))

                if rec.get('max_ma') and rec.get('min_ma'):
                    max_age = float(rec.get('max_ma')) * age_scaler
                    min_age = float(rec.get('min_ma')) * age_scaler
                else:
                    max_age = None
                    min_age = None

                lat = float(rec.get('lat'))
                lon = float(rec.get('lng'))

                occ.update(taxon_id=taxon_id,
                           max_age=max_age,
                           min_age=min_age,
                           age_units=age_units,
                           lat=lat,
                           lon=lon,
                           geog_coords=geog_coords)

                # Call the appropriate output formatter
                if format and format.lower() == 'csv':
                    occ_obj = format_csv(occ)
                else:
                    occ_obj = format_json(occ)

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
    if 'idx' in show_params:
        return jsonify(indicies=id_str)
    else:
        return jsonify(description=desc_obj, records=occ_return)
