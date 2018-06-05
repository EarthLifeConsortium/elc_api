"""Response decoder: The Strategic Environmental Archaeology Database."""


def occurrences(resp_json, return_obj, options):
    """Taxa in time and space."""
    from ..elc import ages

    # Currently SEAD does not support age parameterization
    # The database also does not include age in the occurrence response

    #  factor = ages.set_age_scaler(options=options, db='pbdb')

    for rec in resp_json:

        data = dict()

        data.update(occ_id='sead:loc:{0:d}'.format(rec.get('locale_id')))
        data.update(taxon_id='sead:txn:{0:d}'.format(rec.get('taxon_id')))
        data.update(taxon=rec.get('taxon'))
        data.update(source=rec.get('source'))
        data.update(max_age=None)
        data.update(min_age=None)
        data.update(lat=rec.get('lat'))
        data.update(lon=rec.get('lon'))
        data.update(data_type=None)
        data.update(elevation=None)
        data.update(locale_id=rec.get('locale_id'))

        return_obj.append(data)

    return return_obj
