"""Alternative output generators for ELC endpoints."""


def type_bibjson(refs_json):
    """Format BibJSON return from list of standard JSON objects."""
    refs_bibjson = list()

    for rec in refs_json:
        bib = dict()

        # Add basic reference info
        bib.update(type=rec.get('kind'),
                   year=rec.get('year'),
                   title=rec.get('title'),
                   citation=rec.get('cite'))

        # Add info specific to the journal or book
        bib.update(journal=[{'name': rec.get('journal'),
                             'volume': rec.get('vol'),
                             'pages': rec.get('pages'),
                             'editor': rec.get('editor')}])

        # Add rec locator IDs
        bib.update(identifier=[{'type': 'doi',
                                'id': rec.get('doi')},
                               {'type': 'db_index',
                                'id': rec.get('ref_id')}])

        # Sequentially add authors to the authors block
        bib.update(author=[])
        for author in rec.get('authors'):
            bib['author'].append({'name': author})

        refs_bibjson.append(bib)

    return refs_bibjson


def type_ris(refs_json):
    """Format RIS return from list of standard JSON objects."""
    import yaml

    with open('swagger_server/lookup/ris_mapping.yaml') as f:
        ris_type = yaml.safe_load(f)

    ris = list()

    for rec in refs_json:

        print(rec.get('ref_id'))
        print(rec.get('kind'))
        if rec.get('kind'):
            ris.append('TY  - {0:s}\n'
                       .format(ris_type.get(rec['kind'], ' ')))
        else:
            ris.append('TY  - \n')

        if rec.get('authors'):
            for author in rec['authors']:
                ris.append('AU  - {0:s}\n'.format(author))

        if rec.get('year'):
            ris.append('YR  - {0:s}///\n'.format(str(rec['year'])))

        if rec.get('title'):
            ris.append('TI  - {0:s}\n'.format(rec['title']))

        if rec.get('journal'):
            ris.append('JF  - {0:s}\n'.format(rec['journal']))

        if rec.get('vol_no'):
            ris.append('VL  - {0:s}\n'.format(rec['vol_no']))

        if rec.get('page_range'):
            pages = [x.strip() for x in rec['page_range'].split('-')]
            ris.append('SP  - {0:s}\n'.format(str(pages[0])))
            if len(pages) == 2:
                ris.append('EP  - {0:s}\n'.format(str(pages[1])))

        if rec.get('editor'):
            ris.append('ED  - {0:s}\n'.format(rec['editor']))

        if rec.get('doi'):
            ris.append('DO  - {0:s}\n'.format(rec['doi']))

        if rec.get('cite'):
            ris.append('CP  - {0:s}\n'.format(rec['cite']))

        if rec.get('ref_id'):
            ris.append('ID  - {0:s}\n'.format(rec['ref_id']))

        ris.append('ER  -\n\n')

    return ris
