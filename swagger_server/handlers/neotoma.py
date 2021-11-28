"""Response decoder: Neotoma Paleoecology Database."""


def taxonomy(resp_json, return_obj, options):
    """Extract specific data on taxa from the subquery."""
    import yaml

    # Full ecological group names
    with open('swagger_server/lookup/neotoma_eco_groups.yaml') as f:
        eco_map = yaml.safe_load(f)

    for rec in resp_json.get('data', []):

        data = dict()
        
        data.update(db='neotoma')
        
        # Core return

        if rec.get('taxonid'):
            data.update(taxon_id='neot:txn:{0:d}'
                        .format(rec.get('taxonid')))
        else:
            data.update(taxon_id=None)

        data.update(taxon=rec.get('taxonname'))

        if rec.get('highertaxonid'):
            data.update(parent_id='neot:txn:{0:d}'
                        .format(rec.get('highertaxonid')))
        else:
            data.update(parent_id=None)

        data.update(status=rec.get('status'))

        if rec.get('publicationid'):
            data.update(source='neot:pub:{0:d}'
                        .format(rec.get('publicationid')))
        else:
            data.update(source=None)

        data.update(attribution=rec.get('author'))

        # Not available from Neotoma
        data.update(rank=None)
        data.update(common_name=None)
        data.update(occurrences_count=None)
        data.update(early_interval=None)
        data.update(late_interval=None)
        data.update(subtaxa_count=None)
        data.update(subtaxa_extant=None)
        data.update(environment=None)
        data.update(env_basis=None)
        data.update(mobility=None)
        data.update(habitat=None)
        data.update(diet=None)
        data.update(composition=None)

        # Neotoma only taxonomy fields
        if rec.get('ecolgroup'):
            data.update(ecological_group=eco_map.get(rec.get('ecolgroup')))

        return_obj.append(data)

    return return_obj


def locales(resp_json, return_obj, options):
    """Extract locale data from the subquery."""
    import geojson
    from ..elc import ages, geog
    from statistics import mean

    # Utlity function: if 1st param is '', 0 or None return 2nd param
    def choose(x, y): return x or y

    # Utility function: Choose the greater of two numbers
    def greater(x, y): return x if x > y else y

    factor = ages.set_age_scaler(options=options, db='pbdb')

    for rec in resp_json.get('data', []):

        for dataset in rec.get('dataset'):
            data = dict()
            
            data.update(db='neotoma')
            
            # Dataset level information
            data.update(locale_id='neot:dst:{0:d}'
                        .format(choose(dataset.get('datasetid'), 0)))
            data.update(doi=dataset.get('doi'))

            data.update(source=dataset.get('database'))
            data.update(locale_name=rec.get('site')['sitename'])
            data.update(data_type=dataset.get('datasettype'))
            data.update(occurrences_count=None)
            data.update(site_id='neot:sit:{0:d}'
                        .format(choose(rec.get('site')['siteid'], 0)))

            # Record age (unit scaled)
            if dataset.get('agerange'):

                old = choose(dataset.get('agerange').get('age'),
                             dataset.get('agerange').get('ageold'))
                if old is not None and old >= 0:
                    data.update(max_age=round(old / factor, 5))
                else:
                    data.update(max_age=None)

                yng = choose(dataset.get('agerange').get('age'),
                             dataset.get('agerange').get('ageyoung'))
                if yng is not None and yng >= 0:
                    data.update(min_age=round(yng / factor, 5))
                else:
                    data.update(min_age=None)

            # Paleo and modern coordinates
            if rec.get('site').get('geography'):
                loc = geojson.loads(rec.get('site').get('geography'))
                if loc.get('type').lower() == 'point':
                    modern = [loc.get('coordinates')[1],
                              loc.get('coordinates')[0]]
                else:
                    modern = [loc.get('coordinates')[0][0][1],
                              loc.get('coordinates')[0][0][0]]
                if options.get('geog') == 'paleo':
                    m_age = greater(mean(modern) / 1e6, 1)
                    try:
                        paleo, ref = geog.resolve_geog(lat=modern[0],
                                                       lon=modern[1],
                                                       mean_age=round(m_age))
                        paleo = [round(x, 4) for x in paleo]
                        data.update(lat=paleo[0], lon=paleo[1])
                    except ValueError as err:
                        data.update(lat=modern[0], lon=modern[1])
                else:
                    data.update(lat=modern[0], lon=modern[1])

            # Site elevation
            if rec.get('site').get('altitude'):
                data.update(elevation=rec.get('site').get('altitude'))
            else:
                data.update(elevation=None)

            return_obj.append(data)

    return return_obj


def mobile(resp_json, return_obj, options):
    """Lightweight response."""
    import geojson
    from ..elc import ages, geog
    from statistics import mean

    # Utlity function: Choose the existing, non-empty parameter
    def choose(x, y): return x or y

    # Utility function: Choose the greater of two numbers
    def greater(x, y): return x if x > y else y

    factor = ages.set_age_scaler(options=options, db='neotoma')

    for rec in resp_json.get('data', []):

        data = dict()

        data.update(db='neotoma')
        data.update(occ_id='neot:occ:{0:d}'.format(rec.get('sampleid', 0)))
        
        # Taxonomic information
        if rec.get('sample'):

            data.update(taxon=rec.get('sample').get('taxonname'))
            data.update(taxon_id='neot:txn:{0:d}'
                        .format(rec.get('sample').get('taxonid', 0)))

        # Record age (unit scaled)
        if rec.get('age'):

            old = choose(rec.get('age').get('ageolder'),
                         rec.get('age').get('age'))
            if old and old >= 0:
                data.update(max_age=round(old / factor, 5))
            else:
                data.update(max_age=None)

            yng = choose(rec.get('age').get('ageyounger'),
                         rec.get('age').get('age'))
            if yng and yng >= 0:
                data.update(min_age=round(yng / factor, 5))
            else:
                data.update(min_age=None)

        if rec.get('site'):

            site = rec.get('site')

            # Dataset level information
            data.update(elevation=site.get('altitude'))
            data.update(source=site.get('database'))
            data.update(data_type=site.get('datasettype'))
            if site.get('datasetid'):
                data.update(locale_id='neot:dst:{0:d}'
                            .format(site.get('datasetid', 0)))

            # Paleo and modern coordinates
            if site.get('location'):
                loc = geojson.loads(site.get('location'))
                if loc.get('type').lower() == 'point':
                    modern = [loc.get('coordinates')[1],
                              loc.get('coordinates')[0]]
                else:
                    modern = [loc.get('coordinates')[0][0][1],
                              loc.get('coordinates')[0][0][0]]
                if options.get('geog') == 'paleo':
                    m_age = greater(mean(modern) / 1e6, 1)
                    try:
                        paleo, ref = geog.resolve_geog(lat=modern[0],
                                                       lon=modern[1],
                                                       mean_age=round(m_age))
                        paleo = [round(x, 4) for x in paleo]
                        data.update(lat=paleo[0], lon=paleo[1])
                    except ValueError as err:
                        data.update(lat=modern[0], lon=modern[1])
                else:
                    data.update(lat=modern[0], lon=modern[1])

        return_obj.append(data)

    return return_obj


def occurrences(resp_json, return_obj, options):
    """Extract occurrence data from the subquery."""
    import geojson
    from ..elc import ages, geog
    from statistics import mean

    # Utlity function: Choose the existing, non-empty parameter
    def choose(x, y): return x or y

    # Utility function: Choose the greater of two numbers
    def greater(x, y): return x if x > y else y

    factor = ages.set_age_scaler(options=options, db='neotoma')

    for rec in resp_json.get('data', []):

        data = dict()
        
        data.update(db='neotoma')
        data.update(occ_id='neot:occ:{0:d}'.format(choose(rec.get('occid'), 0)))
        
        # Taxonomic information
        if rec.get('sample'):
            sample = rec.get('sample')
            data.update(taxon=sample.get('taxonname'))
            data.update(taxon_id='neot:txn:{0:d}'
                        .format(choose(sample.get('taxonid'), 0)))

        # Record age (unit scaled)
        if rec.get('age'):

            old = choose(rec.get('age').get('ageolder'),
                         rec.get('age').get('age'))
            if old and old >= 0:
                data.update(max_age=round(old / factor, 5))
            else:
                data.update(max_age=None)

            yng = choose(rec.get('age').get('ageyounger'),
                         rec.get('age').get('age'))
            if yng and yng >= 0:
                data.update(min_age=round(yng / factor, 5))
            else:
                data.update(min_age=None)

        # General site level information
        if rec.get('site'):
            site = rec.get('site')

            # Dataset level information
            data.update(elevation=site.get('altitude'))
            data.update(source=site.get('database'))
            data.update(data_type=site.get('datasettype'))
            if site.get('datasetid'):
                data.update(locale_id='neot:dst:{0:d}'
                            .format(choose(site.get('datasetid'), 0)))
            else:
                data.update(locale_id=None)

            # Paleo and modern coordinates
            if site.get('location'):
                loc = geojson.loads(site.get('location'))
                if loc.get('type').lower() == 'point':
                    modern = [loc.get('coordinates')[1],
                              loc.get('coordinates')[0]]
                else:
                    modern = [loc.get('coordinates')[0][0][1],
                              loc.get('coordinates')[0][0][0]]
                if options.get('geog') == 'paleo':
                    m_age = greater(mean(modern) / 1e6, 1)
                    try:
                        paleo, ref = geog.resolve_geog(lat=modern[0],
                                                       lon=modern[1],
                                                       mean_age=round(m_age))
                        paleo = [round(x, 4) for x in paleo]
                        data.update(lat=paleo[0], lon=paleo[1])
                    except ValueError as err:
                        #  data.update(lat=modern[0], lon=modern[1])
                        data.update(lat='({0:4.2f})'.format(modern[0]),
                                    lon='({0:4.2f})'.format(modern[1]))
                else:
                    data.update(lat=modern[0], lon=modern[1])
            else:
                data.update(lat=None, lon=None)

        return_obj.append(data)

    return return_obj


def references(resp_json, return_obj, options):
    """Extract references from the subquery."""
    pubs = resp_json.get('data')

    # Utlity function: if 1st param is '', 0 or None return 2nd param
    def choose(x, y): return x or y

    for rec in pubs.get('result', []):

        # Available fields
        data = {'db': 'neotoma',
                'year': rec.get('year'),
                'journal': rec.get('journal'),
                'doi': rec.get('doi'),
                'cite': rec.get('citation'),
                'page_range': rec.get('pages'),
                'kind': rec.get('publicationtype')}

        # Reference title
        data.update(title=rec.get('booktitle', rec.get('title')))

        # Reference number
        data.update(ref_id='neot:pub:{0:d}'
                    .format(choose(rec.get('publicationid'), 0)))

        # Publisher information
        if rec.get('city') and rec.get('country'):
            data.update(place='{0:s}, {1:s}'.format(rec.get('city'),
                                                    rec.get('country')))
        else:
            data.update(place=rec.get('country'))

        # Publication volume(number) or edition
        if rec.get('issue') and rec.get('volume'):
            data.update(vol_no='{0:s} ({1:s})'.format(rec.get('volume'),
                                                      rec.get('issue')))
        elif rec.get('volume'):
            data.update(vol_no=rec.get('volume'))

        else:
            data.update(vol_no=rec.get('edition'))

        # Publication authors (not always complete in Neotoma record)
        if rec.get('authors'):
            authors = set()
            for author in rec.get('authors'):
                if author.get('familyname'):
                    surname = '{0:s},'.format(author['familyname'])
                    if author.get('givennames'):
                        names = author['givennames'].split()
                        fi = '{0:s}.'.format(names[0][0])
                        if len(names) > 1:
                            mi = '{0:s}.'.format(names[1][0])
                        else:
                            mi = ''
                    authors.add('{0:s} {1:s} {2:s}'.format(surname, fi, mi))
            author_list = list(authors)
        else:
            author_list = []
        data.update(authors=author_list)

        # Not currently available directly in Neotoma
        data.update(publisher=None, editor=None)

        return_obj.append(data)

    return return_obj


def bbox_filter ( wkt_string, lonmin, latmin, lonmax, latmax ):
    """
    Return a string that will select records from the geographic range
    given in WKT. If four bounding coordinates are given instead, a
    POLYGON() is constructed from them.
    """
    
    if wkt_string:
        return {'loc': wkt_string}

    elif lonmin or latmin or lonmax or latmax:
        pattern = 'POLYGON(({0} {1},{2} {1},{2} {3},{0} {3},{0} {1}))'
        return {'loc': pattern.format(lonmin, latmin, lonmax, latmax)}

    else:
        return {}

