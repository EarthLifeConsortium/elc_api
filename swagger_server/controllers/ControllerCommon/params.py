"""Common parameter parsing functions for the API controllers."""


def id_parse(id_list, db_name):
    """
    Separate database:datatype:id_number from a list.

    :arg db_name: Name of DB to search for in list
    :return e: Badly formatted data in id_list
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
                return 'Incorrect datatype in ID list: ' + str(datatype)

    return id_obj


def set_age(payload, agescale, minage, maxage, db_name):
    """
    Convert relative ages for each database query.

    :arg agescale: Age units to use for search and return
    :arg minage: Most recent age of the record bound
    :arg maxage: Oldest age of the record bound
    :arg db_name: Name of the database for which to convert units

    :return age_scaler: Factor for scaling age returned by DB subquery
    """
    # Native DB age format conversion dict
    age = {'neot': {'yr': 1, 'ka': 1e-03, 'ma': 1e-06},
           'pbdb': {'yr': 1e06, 'ka': 1e03, 'ma': 1}}
    units = agescale.lower()

    if units == 'yr':
        age_scaler = age[db_name][units]
        if minage:
            payload.update(ageyoung=int(minage))
        if maxage:
            payload.update(ageold=int(maxage))
    elif units == 'ka':
        age_scaler = age[db_name][units]
        if minage:
            payload.update(ageyoung=int(minage/age_scaler))
        if maxage:
            payload.update(ageold=int(maxage/age_scaler))
    elif units == 'ma':
        age_scaler = age[db_name][units]
        if minage:
            payload.update(ageyoung=int(minage/age_scaler))
        if maxage:
            payload.update(ageold=int(maxage/age_scaler))
    else:
        return 'Incorrect age scaler: ' + str(agescale)

    return age_scaler


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
    Test if geography is lat/lon rectangle or WKT then set parameter.

    :arg bbox: A list containing geographic parameters
    :arg db_name: Database to parameterize
    """
    if db_name == 'neot':
        payload.update(bbox=bbox)
    elif db_name == 'pbdb':
        if len(bbox) == 4:
            bbox_list = bbox.split(',')
            payload.update(lngmin=bbox_list[0], latmin=bbox_list[1],
                           lngmax=bbox_list[2], latmax=bbox_list[3])
        else:
            payload.update(loc=bbox)
