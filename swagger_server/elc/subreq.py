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


def mobile_req(return_obj, payload, db):
    """Custom multi-part dispach requester."""
    from geojson import Point

    if db == 'pbdb':

        # Retrieve all occurrence data
        route = 'https://paleobiodb.org/data1.2/occs/list.json'
        payload.update(limit=10, show='full')
        try:
            occs, url = trigger(route, payload, db)
        except ValueError as err:
            raise ValueError(err.args[0], err.args[1])

        # Retrieve associated taxonomic data
        route = 'https://paleobiodb.org/data1.2/taxa/single.json'
        for rec in occs.get('records'):

            payload = {'show': 'full,img', 'taxon_name': rec.get('tna')}
            try:
                taxon_resp, url = trigger(route, payload, db)
            except ValueError as err:
                raise ValueError(err.args[0], err.args[1])
            taxon_info = taxon_resp['records'][0]

            mob = {'loc': {},
                   'org': {},
                   'eco': {}}

            # Location block

            geoj = Point((rec['lng'],rec['lat']))
            mob['loc'].update(crd=geoj)

            site_desc = None
            if 'cnm' in rec.keys():
                site_desc = rec['cnm']
            if 'aka' in rec.keys():
                site_desc = '; '.join([site_desc, rec['aka']])
            if site_desc:
                mob['loc'].update(ste=site_desc.replace('\"', '\''))

            place = None
            if 'cc2' in rec.keys():
                place = rec['cc2']
            if 'stp' in rec.keys():
                place = '{0:s}, {1:s}'.format(rec['stp'], place)
            if 'cny' in rec.keys():
                place = '{0:s}, {1:s}'.format(rec['cny'], place)
            if place:
                mob['loc'].update(pla=place)

            age_range = ', '.join([str(rec['eag']),str(rec['lag'])])
            mob['loc'].update(age=age_range)

            # Organism block

            mob['org'].update(txn=rec.get('tna'))
            if 'nm2' in taxon_info.keys():
                mob['org'].update(nam=taxon_info.get('nm2'))
                       
            interval = None
            if 'tei' in taxon_info.keys():
                interval = taxon_info['tei']
            if 'tli' in taxon_info.keys():
                interval = ', '.join([interval, taxon_info['tli']])
            if interval:
                mob['org'].update(itv=interval)

            extant = None
            if 'ext' in taxon_info.keys():
                extant = True if taxon_info['ext'] == 1 else False
            if extant:
                mob['org'].update(ext=extant)

            img_uri = None
            if 'img' in taxon_info.keys():
                base = 'https://paleobiodb.org/data1.2/taxa/thumb.png?id='
                img_uri = ''.join([base, taxon_info['img'][4:]])
            if img_uri:
                mob['org'].update(img=img_uri)

            # Ecology and environment block

            if 'jev' in taxon_info.keys():
                mob['eco'].update(env=taxon_info['jev'])
            if 'jmo' in taxon_info.keys():
                mob['eco'].update(mot=taxon_info['jmo'])
            if 'jlh' in taxon_info.keys():
                mob['eco'].update(hab=taxon_info['jlh'])
            if 'jvs' in taxon_info.keys():
                mob['eco'].update(vis=taxon_info['jvs'])
            if 'jdt' in taxon_info.keys():
                mob['eco'].update(dte=taxon_info['jdt'])
            if 'jre' in taxon_info.keys():
                mob['eco'].update(rep=taxon_info['jre'])
            if 'jon' in taxon_info.keys():
                mob['eco'].update(ont=taxon_info['jon'])
            if 'cct' in rec.keys():
                mob['eco'].update(grp=rec['cct'])

            return_obj.append(mob)

    return return_obj
