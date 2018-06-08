"""Response decoder: The Strategic Environmental Archaeology Database."""


def occurrences(resp_json, return_obj, options):
    """Taxa in time and space."""
    #  from ..elc import ages

    # Currently SEAD does not support age parameterization
    # The database also does not include age in the occurrence response

    #  factor = ages.set_age_scaler(options=options, db='pbdb')

    for rec in resp_json:

        data = dict()

        data.update(occ_id='sead:occ:{0:d}'.format(rec.get('occ_id')))
        data.update(taxon_id='sead:txn:{0:d}'.format(rec.get('taxon_id')))
        data.update(locale_id='sead:dst:{0:d}'.format(rec.get('locale_id')))

        # Family, Genus or Species name
        if rec.get('taxon'):
            name = rec.get('taxon').split()
            if len(name) == 1:
                data.update(taxon=name[0].capitalize())
            else:
                gs_name = ' '.join(name[1:])
                data.update(taxon=gs_name)
        else:
            data.update(taxon=None)

        # Source information
        source = ''
        if rec.get('sample_name'):
            source = 'Sample: {0:s}'.format(str(rec.get('sample_name')))
        if rec.get('locale_name'):
            source = '{0:s}, Site: {1:s}'.format(source,
                                                 rec.get('locale_name'))
        data.update(source=source)

        # Ages not yet available from SEAD
        data.update(max_age=None)
        data.update(min_age=None)

        # Geography (modern coordinates)
        data.update(lat=rec.get('lat'))
        data.update(lon=rec.get('lon'))

        data.update(data_type=None)
        data.update(elevation=None)

        return_obj.append(data)

    return return_obj
