"""Common parameter parsing functions for the API controllers."""


def id_parse(id_list, db_name):
    """
    Separate database:datatype:id_number from a list.
    
    :arg db_name: Name of DB to search for in list
    """
    import re

    id_obj = dict(occ=[], loc=[], ref=[], txn=[])

    for id in id_list:
        database = re.search('^\w+(?=:)', id).group()
        datatype = re.search('(?<=:).+(?=:)', id).group()
        id_num = int(re.search('\d+$', id).group())

        if database.lower() == db_name:
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


def set_age(payload, agescale, minage, maxage, db_name):
    """
    Convert relative ages for each database query

    :arg agescale: Age units to use for search and return
    :arg minage: Most recent age of the record bound
    :arg maxage: Oldest age of the record bound
    :arg db_name: Name of the database for which to convert units
    """
    if agescale and agescale.lower() == 'yr':
        age_scaler = 1
        age_units = 'yr'
        if minage:
            payload.update(ageyoung=int(minage))
        if maxage:
            payload.update(ageold=int(maxage))
    elif agescale and agescale.lower() == 'ka':
        age_scaler = 1e-03
        age_units = 'ka'
        if minage:
            payload.update(ageyoung=int(minage/age_scaler))
        if maxage:
            payload.update(ageold=int(maxage/age_scaler))
    else:
        age_scaler = 1e-06
        age_units = 'ma'
        if minage:
            payload.update(ageyoung=int(minage/age_scaler))
        if maxage:
            payload.update(ageold=int(maxage/age_scaler))

    return age_scaler, age_units


def set_timebound(payload, timerule, db_name):
    """
    Set timescale bounding rules.

    :arg timerule: Bounding rule to apply
    :arg db_name: Database for which to apply rule
    """
    if db_name == 'neot':
        if timerule.lower() == 'major':
            payload.update(agedocontain=0)
        elif timerule.lower() == 'overlap':
            payload.update(agedocontain=1)
    elif db_name == 'pbdb':
        payload.update(timerule=timerule)


def set_georaphy(payload, bbox, db_name):
    """
    Test if geography is lat/lon rectangle or WKT
    and set parameter accordingly.

    :arg bbox: A list containing geographic parameters
    :arg db_name: Database to parameterize
    """
    if len(bbox) == 4:
        bbox_list = bbox.split(',')
        payload.update(lngmin=bbox_list[0], latmin=bbox_list[1],
                       lngmax=bbox_list[2], latmax=bbox_list[3])
    else:
        payload.update(loc=box)
