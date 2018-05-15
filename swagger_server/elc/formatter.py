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
