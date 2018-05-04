"""Custom decoder for Neotoma Paleoecology Database response."""


def locales(resp_json, return_obj, options):
    """Extract locale data from the subquery."""
    import geojson
    from ..elc import ages

    # Utlity function: Choose the existing, non-empty parameter
    def choose(x, y): return x or y

    # Utility function: Choose the greater of two numbers 
    def greater(x, y): return x if x > y else y

    factor = ages.set_age_scaler(options=options, db='pbdb')

    for rec in resp_json.get('data', []):

        for dataset in rec.get('dataset'):
            data = dict()

            # Dataset level information
            data.update(locale_id='neot:dst:{0:d}'
                        .format(dataset.get('datasetid', 0)))
            data.update(doi=dataset.get('doi'))

            data.update(source=dataset.get('database'))
            data.update(locale_name=rec.get('site')['sitename'])
            data.update(data_type=dataset.get('datasettype'))
            data.update(occurrences_count=None)
            data.update(site_id='neot:sit:{0:d}'
                        .format(rec.get('site')['siteid'], 0))

            # Record age (unit scaled)
            if dataset.get('agerange'):

                old = choose(dataset.get('agerange').get('ageold'),
                             dataset.get('agerange').get('age'))
                if old and old >= 0:
                    data.update(max_age=round(old / factor, 5))
                else:
                    data.update(max_age=None)

                yng = choose(dataset.get('agerange').get('ageyoung'),
                             dataset.get('agerange').get('age'))
                if yng and yng >= 0:
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


#  def references(resp, ret_obj, format):
    #  """Reformat data from the Neotoma API call."""
    #  import re

    #  if resp.status_code == 200:
        #  resp_json = resp.json()
        #  if 'data' in resp_json:
            #  for rec in resp_json['data']:

                #  # Format the unique database identifier
                #  pub_id = 'neot:pub:' + str(rec.get('PublicationID'))

                #  # Format author fields
                #  author_list = list()
                #  if 'Authors' in rec:
                    #  for author in rec.get('Authors'):
                        #  author_list.append(author['ContactName'])

                #  # Look for a DOI in the citation string
                #  if 'Citation' in rec:
                    #  doi = re.search('(?<=\[DOI:\ ).+(?=\])',
                                    #  rec.get('Citation'))
                    #  if doi:
                        #  doi = doi.group()
                #  else:
                    #  doi = None

                #  # Build dictionary of bibliographic fields
                #  reference = dict()
                #  reference.update(kind=rec.get('PubType'),
                                 #  year=rec.get('Year'),
                                 #  doi=doi,
                                 #  authors=author_list,
                                 #  ident=pub_id,
                                 #  cite=rec.get('Citation'))

                #  # Format and append parsed record
                #  ret_obj = format_handler(reference, ret_obj, format)

    #  # End subroutine: parse_neot_resp
    #  return len(resp_json['data'])
