"""Use the Requests HTTP library with pervasive error handling."""


def trigger(url_path, payload, db):
    """Primary safe requester method for external database resources."""
    import requests
    from ..elc import config

    try:
        resp = requests.get(url_path,
                            params=payload,
                            timeout=config.get('default', 'timeout'))
        resp.raise_for_status()

    except requests.exceptions.HTTPError as err:
        raise ValueError(resp.status_code, str(err.args[0]))

    except requests.exceptions.SSLError as err:
        raise ValueError(495, str(err.args[0]))

    except requests.exceptions.ConnectionError as err:
        raise ValueError(502, str(err.args[0]))

    except requests.exceptions.Timeout as err:
        raise ValueError(504, str(err.args[0]))

    except requests.exceptions.RequestException as err:
        raise ValueError(500, str(err.args[0]))

    # Check the Content-Type of the return and decode the JSON object

    if 'application/json' not in resp.headers.get('content-type'):
        msg = '{0:s} response is not of type application/json'.format(db)
        raise ValueError(417, msg)

    # Check that serialized JSON object is decodable

    try:
        resp_json = resp.json()

    except ValueError as err:
        msg = '{0:s} JSON decode error: {1:s}'.format(db, err)
        raise ValueError(500, msg)

    return resp_json, resp.url


def mobile_req(payload, db):
    """Custom multi-part dispach requester."""
    from geojson import Point

    mob = dict()

    if db == 'pbdb':

        # Retrieve all occurrence data
        route = 'https://paleobiodb.org/data1.2/occs/list.json'
        try:
            occs, url = trigger(route, payload, db)
        except ValueError as err:
            raise ValueError(err.args[0], err.args[1])

        # Retrieve associated taxonomic data
        route = 'https://paleobiodb.org/data1.2/tax/single.json'
        for rec in occs:

            payload = {'show': 'full,img', 'taxon_name': rec.get('tna')}
            try:
                taxon_info, url = trigger(route, payload, db)
            except ValueError as err:
                raise ValueError(err.args[0], err.args[1])

            mob.update(loc={'crd': geo_point,
                            'ste': site_desc,
                            'pla': place,
                            'age': age_range})

            mob.update(org={'txn': rec.get('')})



            mob.update(eco={'env': taxon_info.get('jev'),
                       mot=taxon_info.get('jmo'),
                       hab=taxon_info.get('jlh'),
                       vis=taxon_info.get('jvs'),
                       dte=taxon_info.get('jdt'),
                       rep=taxon_info.get('jre'),
                       ont=taxon_info.get('jon'),
                       grp=taxon_info.get(''),

                       nam=taxon_info.get('tei tli'))

            
            if 'tei' in taxon_info.keys():
                interval = taxon_info['tei']
            if 'tli' in taxon_info.keys():
                interval = ','.join([interval, taxon_info['tli']])

            if 'ext' in taxon_info.keys():
                extant = True if rec['ext'] == 1 else False

            if 'img' in taxon_info.keys():
                base = 'https://paleobiodb.org/data1.2/taxa/thumb.png?id='
                img_uri = ''.join([base, taxon_info['img'][4:]])
