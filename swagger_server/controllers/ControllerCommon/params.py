"""Common parameter parsing functions for the API controllers."""


def idparse(id_list, db_search_name):
    """
    Separate database:datatype:id_number from a list.
    
    :id_list:list:Formatted IDs as 'db:type:number'
    :db_search_name:string:Name of DB to search for

    """
    import re

    id_obj = dict(occ=[], loc=[], ref=[], txn=[])

    for id in id_list:
        database = re.search('^\w+(?=:)', id).group()
        datatype = re.search('(?<=:).+(?=:)', id).group()
        id_num = int(re.search('\d+$', id).group())

        if database.lower() == db_search_name:
            if datatype.lower() == 'occ':
                id_obj['occ'].append(id_num)
            elif datatype.lower() == 'dst' or datatype.lower() == 'col':
                id_obj['loc'].append(id_num)
            elif datatype.lower() == 'pub' or datatype.lower() == 'ref':
                id_obj['ref'].append(id_num)
            elif datatype.lower() == 'txn':
                id_obj['txn'].append(id_num)
            else:
                error = 'Incorrect datatype in ID list: ' + datatype
                return error

    return id_obj
