"""Alternative output generators for ELC endpoints."""



def type_bibjson(refs_json):
    """
    Format BibJSON return from list of standard JSON objects.
    
    Reference spec at http://okfnlabs.org/bibjson.
    """

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


def type_ris(data):
    fmt_obj = dict()

    return fmt_obj


def type_itis(parents, subtaxa):
    """
    Format full taxonomic hierarchy according to the ITIS data model.

    :arg parents: dict containing upper rank and names
    :arg subtaxa: dict containing lower taxa
    """
    itis = list()

    for rank in parents:
        tsn = 9999
        itis.append('[TU]|' + str(tsn) + '||' + parents[rank] + '|')
    return type_plain(itis)


        #  tsn = 9999
        #  unit_ind1
        #  unit_name1
        #  unit_ind2
        #  unit_name2
        #  unit_ind3
        #  unit_name3
        #  unit_ind4
        #  unit_name4
        #  unnamed_taxon_ind
        #  usage
        #  unacceptability_reason
        #  taxonomic_credibility_rating | taxonomic_completeness_rating | currency_rating | phylo_sort_sequence | initial_time_stamp | parent_tsn || taxon_author_id || hybrid_author_id | kingdom_id | rank_id | uncertain_parent_ind |


def type_plain(data):
    """Return a list of strings as plain text."""
    from flask import Response

    return Response('\n'.join(data),
                    content_type='text/plain; charset=utf-8')
