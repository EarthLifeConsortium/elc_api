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


def mobile_req(return_obj, url_path, payload, db):
    """Dispach multi-part requests and assemble mobile response."""
    from geojson import Point

    if db == 'pbdb':

        import yaml
        with open('swagger_server/lookup/iso_3166_alpha2.yaml') as f:
            cc_map = yaml.safe_load(f)

        # Retrieve all occurrence data
        payload.update(show='methods,coords,paleoloc,loc,coll')
        try:
            occs, url = trigger(url_path, payload, db)
        except ValueError as err:
            raise ValueError(err.args[0], err.args[1])

        # Return if no occurrences found for given parameters
        if 'records' not in occs.keys():
            return return_obj

        # Build taxa lookup dictionary
        tax_base = 'https://paleobiodb.org/data1.2/taxa/list.json'

        # Taxa named, perform recursive search on DB to get details
        if payload.get('base_name'):
            tax_payload = {'show': 'full,img',
                           'base_name': payload['base_name']}
            try:
                taxon_resp, url = trigger(tax_base, tax_payload, db)
            except ValueError as err:
                raise ValueError(err.args[0], err.args[1])

        # Only geography named, parameterize taxa from occ response
        else:
            taxa = set()
            for rec in occs.get('records'):
                if 'tna' in rec:
                    taxa.add(rec.get('tna'))
            taxa_list = ','.join(taxa)

            tax_payload = {'show': 'full,img',
                           'taxon_name': taxa_list}
            try:
                taxon_resp, url = trigger(tax_base, tax_payload, db)
            except ValueError as err:
                raise ValueError(err.args[0], err.args[1])

        # Reformat taxa return into a nested dict
        taxa_table = dict()
        for rec in taxon_resp['records']:
            if 'nam' in rec.keys():
                taxa_table[rec['nam']] = rec

        # Build mobile return
        for rec in occs.get('records'):

            if rec.get('tna'):
                taxon_info = taxa_table[rec['tna']]
            else:
                continue

            mob = {'src': 'https://paleobiodb.org',
                   'loc': {},
                   'org': {},
                   'eco': {}}

            # Location block

            if 'lng' in rec.keys() and 'lat' in rec.keys():
                crs = {'type': 'name',
                       'properties': {'name': 'EPSG:4326'}}
                geoj = str(Point(([round(rec['lng'], 3),
                                   round(rec['lat'], 3)]), crs=crs))
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
                country = cc_map.get(rec['cc2'])
                if country:
                    place = country
                else:
                    place = ''
            if 'stp' in rec.keys():
                place = '{0:s}, {1:s}'.format(rec['stp'], place)
            if 'cny' in rec.keys():
                place = '{0:s}, {1:s}'.format(rec['cny'], place)
            if place:
                mob['loc'].update(pla=place)

            age_range = ', '.join([str(rec['eag']), str(rec['lag'])])
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

            if 'ext' in taxon_info.keys():
                extant = 'extant' if taxon_info['ext'] == 1 else 'extinct'
                mob['org'].update(sts=extant)

            if 'img' in taxon_info.keys():
                base = 'https://paleobiodb.org/data1.2/taxa/thumb.png?id='
                img_uri = ''.join([base, taxon_info['img'][4:]])
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
                mob['eco'].update(typ=rec['cct'])
            if 'jec' in taxon_info.keys():
                mob['eco'].update(grp=taxon_info['jec'])

            return_obj.append(mob)

    elif db == 'neotoma':

        import yaml
        with open('swagger_server/lookup/neotoma_eco_groups.yaml') as f:
            eco_map = yaml.safe_load(f)
        with open('swagger_server/lookup/neotoma_taxa_groups.yaml') as f:
            taxa_map = yaml.safe_load(f)
        with open('swagger_server/lookup/neotoma_geopolunits.yaml') as f:
            geo_map = yaml.safe_load(f)

        # Build GeoPoliticalUnit index
        base = 'http://api-dev.neotomadb.org/v2.0/data/'
        route = 'dbtables/sitegeopolitical'
        uri = ''.join([base, route])
        params = ''
        try:
            site_gpu, url = trigger(uri, params, db)
        except ValueError as err:
            raise ValueError(err.args[0], err.args[1])
        last_site = ''
        geo_units = dict()
        for rec in site_gpu['data']:
            site = rec.get('siteid')
            if site == last_site:
                geo_units[site].append(rec.get('geopoliticalid'))
            else:
                geo_units[site] = [rec.get('geopoliticalid')]
            last_site = site

        # Retrieve all occurrence data
        try:
            occs, url = trigger(url_path, payload, db)
        except ValueError as err:
            raise ValueError(err.args[0], err.args[1])

        # Return if no occurrences found for given parameters
        if 'data' not in occs:
            return return_obj

        # Build taxa lookup dictionary
        tax_base = 'http://api-dev.neotomadb.org/v2.0/data/taxa'

        # Taxa named, perform recursive search on DB to get details
        if payload.get('taxonname'):
            tax_payload = {'taxonname': payload['taxonname'],
                           'lower': 'true',
                           'limit': 999999}
            try:
                taxon_resp, url = trigger(tax_base, tax_payload, db)
            except ValueError as err:
                raise ValueError(err.args[0], err.args[1])

        # Only geography named, parameterize taxa from occ response
        else:
            taxa = set()
            for rec in occs.get('data'):
                if 'sample' in rec:
                    if 'taxonid' in rec['sample']:
                        taxa.add(str(rec['sample'].get('taxonid')))
            taxa_list = ','.join(taxa)
            tax_payload = {'taxonid': taxa_list, 'limit': 999999}

            try:
                taxon_resp, url = trigger(tax_base, tax_payload, db)
            except ValueError as err:
                raise ValueError(err.args[0], err.args[1])

        # Reformat taxa return into a nested dict
        taxa_table = dict()
        for rec in taxon_resp['data']:
            if 'taxonid' in rec.keys():
                taxa_table[rec['taxonid']] = rec

        # Build mobile return
        for rec in occs.get('data'):

            if 'sample' in rec:
                if 'taxonid' in rec['sample']:
                    taxon_info = taxa_table[rec['sample']['taxonid']]
                else:
                    continue
            else:
                continue

            mob = {'src': 'https://neotomadb.org',
                   'loc': {},
                   'org': {},
                   'eco': {}}

            # Process occurrences return

            if 'site' in rec:
                if rec['site'].get('location'):
                    mob['loc'].update(crd=rec['site']['location'])

                if rec['site'].get('sitename'):
                    mob['loc'].update(ste=rec['site']['sitename'])

                if rec['site'].get('datasettype'):
                    mob['eco'].update(typ=rec['site']['datasettype'])

                siteid = rec['site']['siteid']
                if siteid:
                    place = list()
                    for gpu in reversed(geo_units[siteid]):
                        loc_level = geo_map.get(gpu)
                        if loc_level:
                            place.append(loc_level)
                    if place:
                        mob['loc'].update(pla=', '.join(place))

            if 'sample' in rec:
                mob['org'].update(txn=rec['sample']['taxonname'])

            if 'age' in rec:
                if rec['age'].get('age'):
                    age_range = ', '.join([str(rec['age']['age']),
                                           str(rec['age']['age'])])
                    mob['loc'].update(age=age_range)

                elif (rec['age'].get('ageolder') and
                      rec['age'].get('ageyounger')):
                    age_range = ', '.join([str(rec['age']['ageolder']),
                                           str(rec['age']['ageyounger'])])
                    mob['loc'].update(age=age_range)

            # Process taxon return

            group = None
            if 'ecolgroup' in taxon_info.keys():
                ecolgroup = eco_map.get(taxon_info['ecolgroup'])
                if ecolgroup:
                    group = ecolgroup
            if 'taxagroup' in taxon_info.keys():
                if group:
                    taxagroup = taxa_map.get(taxon_info['taxagroup'])
                    if taxagroup:
                        group = ', '.join([group, taxagroup])
            if group:
                mob['eco'].update(grp=group)

            if 'status' in taxon_info.keys():
                mob['org'].update(sts=taxon_info['status'])

            return_obj.append(mob)

    return return_obj
