"""Use the Requests HTTP library with pervasive error handling."""

import re

def trigger(url_path, payload, db):
    """Primary safe requester method for external database resources."""
    import requests
    from ..elc import config
    
    try:
        resp = requests.get(url_path,
                            params=payload,
                            timeout=config.get('default', 'timeout'))
        print("Subrequest [" + db + '] ' + clean_url(resp.url))
        resp.raise_for_status()
    
    except requests.exceptions.HTTPError as err:
        print("  HTTP Error: ", str(err.args[0]))
        raise ValueError(resp.status_code, str(err.args[0]))
    
    except requests.exceptions.SSLError as err:
        print("  SSL Error: ", str(err.args[0]))
        raise ValueError(495, str(err.args[0]))
    
    except requests.exceptions.ConnectionError as err:
        print("  Connection Error: ", str(err.args[0]))
        raise ValueError(502, str(err.args[0]))
    
    except requests.exceptions.Timeout as err:
        print("  Timeout: ", str(err.args[0]))
        raise ValueError(504, str(err.args[0]))
    
    except requests.exceptions.RequestException as err:
        print("  Request Error: ", str(err.args[0]))
        raise ValueError(500, str(err.args[0]))
    
    # Check the Content-Type of the return and decode the JSON object

    if 'application/json' not in resp.headers.get('content-type'):
        return dict(), resp.url
        # msg = '{0:s} response is not of type application/json'.format(db)
        # raise ValueError(417, msg)

    # Check that serialized JSON object is decodable

    try:
        resp_json = resp.json()

    except ValueError as err:
        msg = '{0:s} JSON decode error: {1:s}'.format(db, err)
        raise ValueError(500, msg)

    return resp_json, resp.url


def clean_url ( url ):
    
    return re.sub('%[0-9A-F][0-9A-F]', substitute_codes, url)


def substitute_codes ( match ):

    if match.group() == '%28':
        return '('

    elif match.group() == '%29':
        return ')'

    elif match.group() == '%2C':
        return ','

    else:
        return match.group()


def mobile_req(return_obj, url_path, payload, db):
    """Dispatch multi-part requests and assemble mobile response."""
    from geojson import Point
    from time import time

    # Request occurrences from The Paleobiology Database
    if db == 'pbdb':
        pbdb_t0 = time()

        #  import yaml
        #  with open('swagger_server/lookup/iso_3166_alpha2.yaml') as f:
        #      cc_map = yaml.safe_load(f)

        # Retrieve all occurrence data
        payload.update(show='methods,coords,paleoloc,loc,coll',
                       extids=False)

        occ_t0 = time()

        try:
            occs, url = trigger(url_path, payload, db)
        except ValueError as err:
            raise ValueError(err.args[0], err.args[1])

        pbdb_occ_call = round(time() - occ_t0, 3)
        # print('PBDB Occ call = ' + str(pbdb_occ_call))

        # Return if no occurrences found for given parameters
        if 'records' not in occs.keys():
            return return_obj
        elif occs['records'] == []:
            return return_obj

        # Build taxa lookup dictionary
        tax_base = 'https://paleobiodb.org/data1.2/taxa/list.json'

        # Taxa named, perform recursive search on DB to get details
        if payload.get('base_name'):
            tax_payload = {'show': 'full,img',
                           'extids': False,
                           'base_name': payload['base_name']}

            taxa_t0 = time()

            try:
                taxon_resp, url = trigger(tax_base, tax_payload, db)
            except ValueError as err:
                raise ValueError(err.args[0], err.args[1])

            pbdb_taxa_call = round(time() - taxa_t0, 3)
            # print('PBDB Taxa call = ' + str(pbdb_taxa_call))

            if 'records' not in taxon_resp.keys():
                return return_obj
            elif taxon_resp['records'] == []:
                return return_obj

            taxa = set()
            for rec in taxon_resp['records']:
                if rec.get('oid'):
                    taxa.add(rec['oid'])

        # Only geography named, parameterize taxa from occ response
        else:
            taxa = set()
            for rec in occs.get('records'):
                if 'tid' in rec:
                    taxa.add(rec.get('tid'))
            taxa_list = ','.join([str(x) for x in taxa])

            tax_payload = {'show': 'full,img',
                           'extids': False,
                           'taxon_id': taxa_list}
            try:
                taxon_resp, url = trigger(tax_base, tax_payload, db)
            except ValueError as err:
                raise ValueError(err.args[0], err.args[1])

        # Reformat taxa return into a nested dict
        taxa_table = dict()
        for rec in taxon_resp['records']:
            if 'oid' in rec.keys():
                if rec['oid'] in taxa:
                    taxa_table[rec['oid']] = rec

        # Build mobile return
        for rec in occs.get('records'):

            if rec.get('tid'):
                if rec['tid'] in taxa_table.keys():
                    taxon_info = taxa_table[rec['tid']]
            else:
                continue

            if rec.get('oid'):
                occ_id = 'pbdb:occ:{0:d}'.format(rec['oid'])
            else:
                occ_id = 'pbdb:occ:0'

            mob = {'src': occ_id,
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
                site_desc = '; '.join([str(site_desc), str(rec['aka'])])
            if site_desc:
                mob['loc'].update(ste=site_desc.replace('\"', '\''))

            place = None
            if 'cc2' in rec.keys():
                place = rec['cc2']
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
                img_uri = ''.join([base, str(taxon_info['img'])])
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

        pbdb_time = round(time() - pbdb_t0, 3)
        # print('PBDB other processing = ' +
        #       str(round(pbdb_time - pbdb_occ_call - pbdb_taxa_call, 4)))
        # print('PBDB total runtime = ' + str(pbdb_time))

    # Request occurrences from the Neotoma Paleoecology Database
    elif db == 'neotoma':
        neot_t0 = time()

        #  import yaml
        #  with open('swagger_server/lookup/neotoma_eco_groups.yaml') as f:
        #      eco_map = yaml.safe_load(f)
        #  with open('swagger_server/lookup/neotoma_taxa_groups.yaml') as f:
        #      taxa_map = yaml.safe_load(f)
        #  with open('swagger_server/lookup/neotoma_geopolunits.yaml') as f:
        #      geo_map = yaml.safe_load(f)

        #  # Build GeoPoliticalUnit index
        #  base = 'http://api.neotomadb.org/v2.0/data/'
        #  route = 'dbtables/sitegeopolitical'
        #  uri = ''.join([base, route])
        #  params = ''
        #  try:
        #      site_gpu, url = trigger(uri, params, db)
        #  except ValueError as err:
        #      raise ValueError(err.args[0], err.args[1])
        #  last_site = ''
        #  geo_units = dict()
        #  for rec in site_gpu['data']:
        #      site = rec.get('siteid')
        #      if site == last_site:
        #          geo_units[site].append(rec.get('geopoliticalid'))
        #      else:
        #          geo_units[site] = [rec.get('geopoliticalid')]
        #      last_site = site

        # Retrieve all occurrence data

        occ_t0 = time()

        try:
            occs, url = trigger(url_path, payload, db)
        except ValueError as err:
            raise ValueError(err.args[0], err.args[1])

        neot_occ_call = round(time() - occ_t0, 3)
        # print('Neotoma Occ call = ' + str(round(time() - occ_t0, 3)))

        # Return if no occurrences found for given parameters
        if 'data' not in occs:
            return return_obj

        # Build taxa lookup dictionary
        tax_base = 'http://api.neotomadb.org/v2.0/data/taxa/'

        # Taxa named, perform recursive search on DB to get details
        if payload.get('taxonname'):
            tax_payload = {'taxonname': payload['taxonname'],
                           'lower': 'true',
                           'limit': 999999}

            taxa_t0 = time()

            try:
                taxon_resp, url = trigger(tax_base, tax_payload, db)
            except ValueError as err:
                raise ValueError(err.args[0], err.args[1])

            neot_taxa_call = round(time() - taxa_t0, 3)
            # print('Neotoma taxa call = ' + str(neot_taxa_call))

            if 'data' not in taxon_resp.keys():
                return return_obj
            elif taxon_resp['data'] == []:
                return return_obj

            taxa = set()
            for rec in taxon_resp['data']:
                if rec.get('taxonid'):
                    taxa.add(rec['taxonid'])

        # Only geography named, parameterize taxa from occ response
        else:
            taxa = set()
            for rec in occs.get('data'):
                if 'sample' in rec:
                    if 'taxonid' in rec['sample']:
                        taxa.add(rec['sample'].get('taxonid'))
            taxa_list = ','.join(str(x) for x in taxa)
            tax_payload = {'taxonid': taxa_list, 'limit': 999999}

            try:
                taxon_resp, url = trigger(tax_base, tax_payload, db)
            except ValueError as err:
                raise ValueError(err.args[0], err.args[1])

        # Reformat taxa return into a nested dict
        taxa_table = dict()
        for rec in taxon_resp['data']:
            if 'taxonid' in rec.keys():
                if rec['taxonid'] in taxa:
                    taxa_table[rec['taxonid']] = rec

        # Build mobile return
        for rec in occs.get('data'):

            if 'sample' in rec:
                if 'taxonid' in rec['sample']:
                    if rec['sample']['taxonid'] in taxa_table.keys():
                        taxon_info = taxa_table[rec['sample']['taxonid']]
                    else:
                        continue
                else:
                    continue
            else:
                continue

            if rec.get('occid'):
                occ_id = 'neot:occ:{0:d}'.format(rec['occid'])
            else:
                occ_id = 'neot:occ:0'

            mob = {'src': occ_id,
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

                siteid = rec['site'].get('siteid')
                mob['loc'].update(pla=None)

            if 'sample' in rec:
                mob['org'].update(txn=rec['sample']['taxonname'])

            if 'age' in rec:
                if rec['age'].get('age'):
                    age_range = ', '.join([str(rec['age']['age']),
                                           str(rec['age']['age'])])
                    mob['loc'].update(age=age_range)

                elif ((rec['age'].get('ageolder')
                      and rec['age'].get('ageyounger'))):
                    age_range = ', '.join([str(rec['age']['ageolder']),
                                           str(rec['age']['ageyounger'])])
                    mob['loc'].update(age=age_range)

            # Process taxon return

            group = None
            if 'ecolgroup' in taxon_info.keys():
                ecolgroup = taxon_info['ecolgroup']
                if ecolgroup:
                    group = ecolgroup
            if 'taxagroup' in taxon_info.keys():
                if group:
                    taxagroup = taxon_info['taxagroup']
                    if taxagroup:
                        group = ', '.join([group, taxagroup])
            if group:
                mob['eco'].update(grp=group)

            if 'status' in taxon_info.keys():
                mob['org'].update(sts=taxon_info['status'])

            return_obj.append(mob)

        total_time = time() - neot_t0
        # print('Neotoma other processing = '
        # + str(round(total_time - neot_occ_call - neot_taxa_call, 4)))
        # print('Neotoma runtime = ' + str(round(time() - neot_t0, 3)))
    return return_obj
