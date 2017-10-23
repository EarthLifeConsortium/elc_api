"""Common parameter parsing functions for the API controllers."""


def idparse(id_list, db_search_name):
    """Separate database:datatype:id_number from a list."""
    import re

    occs, locs, refs, txns = [], [], [], []

    for id in id_list:
        database = re.search('^\w+(?=:)', id).group()
        datatype = re.search('(?<=:).+(?=:)', id).group()
        id_num = int(re.search('\d+$', id).group())

        if database.lower() == db_search_name:
            if datatype.lower() == 'occ':
                occs.append(id_num)
            elif datatype.lower() == 'dst' or datatype.lower() == 'col':
                locs.append(id_num)
            elif datatype.lower() == 'pub' or datatype.lower() == 'ref':
                refs.append(id_num)
            elif datatype.lower() == 'txn':
                txns.append(id_num)
            else:
                error = 'Incorrect datatype in ID list: ' + datatype
                return error

    return occs, locs, refs, txns
