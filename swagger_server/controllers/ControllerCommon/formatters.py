"""Common output generators functions for the API controllers."""


def type_json(data):
    """Format data as a JSON return."""
    fmt_obj = dict()

    for key in data:
        fmt_obj.update({key: data[key]})

    return fmt_obj


def type_csv(data):
    """Format data as a tabular CSV file."""
    fmt_obj = dict()

    return fmt_obj


def type_bibjson(data):
    fmt_obj = dict()

    return fmt_obj


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
