"""Response decoder: The Paleobiology Database (PBDB)."""


def taxonomy(resp_json, return_obj, options):
    """Extract specific data on taxa from the subquery."""
    import yaml

    # Named taxonomic ranks
    with open('swagger_server/lookup/pbdb_taxa_ranks.yaml') as f:
        rank_map = yaml.safe_load(f)

    for rec in resp_json.get('records', []):

        data = dict()

        # Core return

        data.update(taxon_id='pbdb:{0:s}'.format(rec.get('oid', 'txn:0')))
        data.update(taxon=rec.get('nam'))
        data.update(parent_id='pbdb:{0:s}'.format(rec.get('par', 'txn:0')))

        try:
            status = 'extant' if bool(int(rec.get('ext'))) else 'extinct'
            data.update(status=status)
        except TypeError as e:
            data.update(status=None)

        data.update(source='pbdb:{0:s}'.format(rec.get('rid', 'ref:0')))
        data.update(attribution=rec.get('att'))

        # PBDB only taxonomy fields
        data.update(rank=rank_map.get(rec.get('rnk')))
        data.update(common_name=rec.get('nm2'))
        data.update(occurrences_count=rec.get('noc'))
        data.update(early_interval=rec.get('tei'))
        data.update(late_interval=rec.get('tli'))
        data.update(subtaxa_count=rec.get('siz'))
        data.update(subtaxa_extant=rec.get('exs'))
        data.update(environment=rec.get('jev'))
        data.update(env_basis=rec.get('jec'))
        data.update(mobility=rec.get('jmo'))
        data.update(habitat=rec.get('jlh'))
        data.update(diet=rec.get('jdt'))
        data.update(composition=rec.get('jco'))

        # Not available from PBDB
        data.update(ecological_group=None)

        return_obj.append(data)

    return return_obj


def locales(resp_json, return_obj, options):
    """Extract locale data from the subquery."""
    from ..elc import ages

    factor = ages.set_age_scaler(options=options, db='pbdb')

    for rec in resp_json.get('records', []):

        data = dict()

        data.update(locale_id='pbdb:{0:s}'.format(rec.get('oid', 'col:0')))
        data.update(doi=None)

        data.update(source='pbdb:{0:s}'.format(rec.get('rid', 'ref:0')))
        data.update(locale_name=rec.get('nam'))
        data.update(data_type=rec.get('cct', 'general faunal/floral'))
        data.update(occurrences_count=rec.get('noc'))
        data.update(site_id=None)

        data.update(max_age=round(rec.get('eag') / factor, 4))
        data.update(min_age=round(rec.get('lag') / factor, 4))

        if options.get('geog') == 'paleo':
            data.update(lat=rec.get('pla'))
            data.update(lon=rec.get('pln'))
        else:
            data.update(lat=rec.get('lat'))
            data.update(lon=rec.get('lng'))

        # Elevation not yet available through PBDB API
        data.update(elevation=None)

        return_obj.append(data)

    return return_obj


def mobile(resp_json, return_obj, options):
    """Lightweight response."""
    from ..elc import ages

    factor = ages.set_age_scaler(options=options, db='pbdb')

    for rec in resp_json.get('records', []):

        data = dict()

        data.update(occ_id='pbdb:{0:s}'.format(rec.get('oid', 'occ:0')))

        data.update(taxon=rec.get('tna'))
        data.update(taxon_id='pbdb:{0:s}'.format(rec.get('tid', 'txn:0')))

        data.update(max_age=round(rec.get('eag') / factor, 4))
        data.update(min_age=round(rec.get('lag') / factor, 4))

        data.update(source='pbdb:{0:s}'.format(rec.get('rid', 'ref:0')))
        data.update(data_type=rec.get('cct', 'general faunal/floral'))
        data.update(locale_id='pbdb:{0:s}'.format(rec.get('cid', 'col:0')))

        if options.get('geog') == 'paleo':
            data.update(lat=rec.get('pla'))
            data.update(lon=rec.get('pln'))
        else:
            data.update(lat=rec.get('lat'))
            data.update(lon=rec.get('lng'))

        # Elevation not yet available through PBDB API
        data.update(elevation=None)

        return_obj.append(data)

    return return_obj


def occurrences(resp_json, return_obj, options):
    """Extract occurrence data from the subquery."""
    from ..elc import ages

    factor = ages.set_age_scaler(options=options, db='pbdb')

    for rec in resp_json.get('records', []):

        data = dict()

        data.update(occ_id='pbdb:{0:s}'.format(rec.get('oid', 'occ:0')))

        data.update(taxon=rec.get('tna'))
        data.update(taxon_id='pbdb:{0:s}'.format(rec.get('tid', 'txn:0')))

        data.update(max_age=round(rec.get('eag') / factor, 4))
        data.update(min_age=round(rec.get('lag') / factor, 4))

        data.update(source='pbdb:{0:s}'.format(rec.get('rid', 'ref:0')))
        data.update(data_type=rec.get('cct', 'general faunal/floral'))
        data.update(locale_id='pbdb:{0:s}'.format(rec.get('cid', 'col:0')))

        if options.get('geog') == 'paleo':
            data.update(lat=rec.get('pla'))
            data.update(lon=rec.get('pln'))
        else:
            data.update(lat=rec.get('lat'))
            data.update(lon=rec.get('lng'))

        # Elevation not yet available through PBDB API
        data.update(elevation=None)

        return_obj.append(data)

    return return_obj


def references(resp_json, return_obj, options):
    """Extract references data from the subquery."""
    for rec in resp_json.get('records', []):

        # Directly mapped bibliographic data
        data = {'title': rec.get('tit'),
                'kind': rec.get('pty'),
                'year': rec.get('pby'),
                'journal': rec.get('pbt'),
                'editor': rec.get('eds'),
                'doi': rec.get('doi'),
                'cite': rec.get('ref'),
                'publisher': rec.get('pbl'),
                'place': rec.get('pbc')}

        # Reference number
        data.update(ref_id='pbdb:{0:s}'.format(rec.get('oid', 'occ:0')))

        # Publication volume(number)
        if rec.get('vno'):
            if rec.get('vol'):
                data.update(vol_no='{0:s} ({1:s})'.format(rec.get('vol'),
                                                          rec.get('vno')))
            else:
                data.update(vol_no=rec.get('vno'))
        else:
            data.update(vol_no=None)

        # Reference page range as first-last
        if rec.get('pgf'):
            if rec.get('pdl'):
                data.update(page_range='{0:s}-{1:s}'.format(rec.get('pgf'),
                                                            rec.get('pgl')))
            else:
                data.update(page_range=rec.get('pgf'))
        else:
            data.update(page_range=None)

        # Build author list
        author_list = list()
        if rec.get('al1'):
            author1 = rec.get('al1').replace(',', '')
            if rec.get('ai1'):
                author1 = '{0:s}, {1:s}'.format(author1, rec.get('ai1'))
            author_list.append(author1)
        if rec.get('al2'):
            author2 = rec.get('al2').replace(',', '')
            if rec.get('ai2'):
                author2 = '{0:s}, {1:s}'.format(author2, rec.get('ai2'))
            author_list.append(author2)
        if rec.get('oau'):
            more_authors = rec.get('oau').split(', ')
            for next_author in more_authors:
                surname = next_author.split()[-1]
                given = next_author[0:next_author.find(surname)-1]
                name = '{0:s}, {1:s}'.format(surname, given)
                name = name.replace(', and', ', ')
                author_list.append(name)
        data.update(authors=author_list)

        return_obj.append(data)

    return return_obj
