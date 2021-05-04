"""Response decoder: The Strategic Environmental Archaeology Database."""

import connexion
import re
from ..elc import config, subreq


def taxonomy(resp_json, return_obj, options):
    """Extract specific data on taxa from the subquery."""
    
    for rec in resp_json:

        data = dict()
        
        # Determine the taxon rank and fill in the appropriate fields

        if "species" in rec:
            data.update(taxon_id='sead:txn:spc:{}'.format(rec.get('taxon_id', '0')))
            if rec.get('taxa_tree_genera'):
                data.update(taxon=' '.join([rec.get('taxa_tree_genera').get('genus_name', '???'),
                                            rec.get('species', 'sp.')]))
            else:
                data.update(taxon=' '.join([rec.get('genus_name', '???'),
                                            rec.get('species', 'sp.')]))
            data.update(rank='species')
            data.update(parent_id='sead:txn:gen:{}'.format(rec.get('genus_id', '0')))
        
        elif "genus_name" in rec:
            data.update(taxon_id='sead:txn:gen:{}'.format(rec.get('genus_id', '0')))
            data.update(taxon=rec.get('genus_name', '???'))
            data.update(rank='genus')
            data.update(parent_id='sead:txn:fam:{}'.format(rec.get('family_id', '0')))

        elif "family_name" in rec:
            data.update(taxon_id='sead:txn:fam:{}'.format(rec.get('family_id', '0')))
            data.update(taxon=rec.get('family_name', '???'))
            data.update(rank='family')
            data.update(parent_id='sead:txn:ord:{}'.format(rec.get('order_id', '0')))
        
        elif "order_name" in rec:
            data.update(taxon_id='sead:txn:ord:{}'.format(rec.get('order_id', '0')))
            data.update(taxon=rec.get('order_name', '???'))
            data.update(rank='order')

        else:
            data.update(rank='???')
            data.update(taxon='???')
        
        return_obj.append(data)
    
    return return_obj


def occurrences(resp_json, return_obj, options):
    """Taxa in time and space."""
    #  from ..elc import ages

    # Currently SEAD does not support age parameterization
    # The database also does not include age in the occurrence response

    #  factor = ages.set_age_scaler(options=options, db='pbdb')

    for rec in resp_json:

        data = dict()
        
        data.update(occ_id='sead:occ:{0:d}'.format(rec.get('occ_id')))
        data.update(taxon_id='sead:txn:spc:{0:d}'.format(rec.get('taxon_id')))
        data.update(locale_id='sead:loc:{0:d}'.format(rec.get('locale_id')))
        
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


def locales(resp_json, return_obj, options):
    """Locations in space and time at which data was collected."""

    for rec in resp_json:

        data = dict()

        data.update(locale_id='sead:loc:{0:d}'.format(rec.get('locale_id')))
        
        if rec.get('doi'):
            data.update(doi=rec.get('doi'))
        if rec.get('locale_name'):
            data.update(locale_name=rec.get('locale_name'))
        if rec.get('data_type'):
            data.update(data_type=rec.get('data_type'))
        if rec.get('occurrences_count'):
            data.update(occurrences_count=rec.get('occurrences_count'))
        if rec.get('site_id'):
            data.update(site_id='sead:sit:{0:d}'.format(rec.get('site_id')))
        
        if rec.get('max_age'):
            data.update(max_age=rec.get('max_age'))
        if rec.get('min_age'):
            data.update(min_age=rec.get('min_age'))
        
        if rec.get('lat'):
            data.update(lat=rec.get('lat'))
        if rec.get('lon'):
            data.update(lon=rec.get('lon'))
        if rec.get('elevation'):
            data.update(elevation=rec.get('elevation'))
        
        return_obj.append(data)

    return return_obj


def taxon_lookup(taxon_name):
    """Given a taxon name, return its record if it is present in the SEAD database at any rank."""
    
    return_list = list()
    
    # Split the name on commas, and then look up each item.
    
    for item in re.split("\s*,\s*", taxon_name):
        
        # If the name contains a space, it is a species name.
        
        if item.count(' '):
            
            component = re.split("\s+", item)
            genus_name = component[0].replace('.', '*')
            species_name = component[1].replace('.', '*')
            
            lookup = dict(species='ilike.' + species_name,
                        genus='ilike.' + genus_name,
                        select='species,genus_name:genus,genus_id,taxon_id')
            
            uri_path = ''.join([config.get('resource_api', 'sead'), '_taxa_alphabetically'])
            
            resp_json, api_call = subreq.trigger(uri_path, lookup, 'sead')
            
            return_list.extend(resp_json)
            continue
        
        # Otherwise, we look for it in the other taxonomy tables. We start by checking the genera
        # because a single component name is more likely to be a genus than anything else.
        
        lookup = dict(genus_name='ilike.' + item)
        
        uri_path = ''.join([config.get('resource_api', 'sead'), 'taxa_tree_genera'])
        
        resp_json, api_call = subreq.trigger(uri_path, lookup, 'sead')
        
        if len(resp_json):
            return_list.extend(resp_json)
        
        # If we don't find the name in the taxa_tree_genera table, we check for a
        # family next.
        
        lookup = dict(family_name='ilike.' + item)
        
        uri_path = ''.join([config.get('resource_api', 'sead'), 'taxa_tree_families'])
        
        resp_json, api_call = subreq.trigger(uri_path, lookup, 'sead')
        
        if len(resp_json):
            return_list.extend(resp_json)
        
        # If the lookup in the family table fails, then check for an order.
        
        lookup = dict(order_name='ilike.' + item)
        
        uri_path = ''.join([config.get('resource_api', 'sead'), 'taxa_tree_orders'])
        
        resp_json, api_call = subreq.trigger(uri_path, lookup, 'sead')
        
        if len(resp_json):
            return_list.extend(resp_json)

    # Now return whatever results we have collected. We have no way to return more than one API
    # call, so we just return the last one executed.
    
    return return_list, api_call



def taxon_id_lookup(params):
    """Given one or more of the parameters taxon_id, genus_id, family_id, order_id: return matching records."""
    
    return_list = list()

    if params.get('taxon_id'):

        lookup = dict(taxon_id='in.(' + params.get('taxon_id') + ')',
                      select='*,taxa_tree_genera(genus_name)')

        uri_path = ''.join([config.get('resource_api', 'sead'), 'taxa_tree_master'])

        resp_json, api_call = subreq.trigger(uri_path, lookup, 'sead')

        return_list.extend(resp_json)

    if params.get('genus_id'):

        lookup = dict(genus_id='in.(' + params.get('genus_id') + ')')

        uri_path = ''.join([config.get('resource_api', 'sead'), 'taxa_tree_genera'])

        resp_json, api_call = subreq.trigger(uri_path, lookup, 'sead')

        return_list.extend(resp_json)
        
    if params.get('family_id'):

        lookup = dict(family_id='in.(' + params.get('family_id') + ')')

        uri_path = ''.join([config.get('resource_api', 'sead'), 'taxa_tree_families'])

        resp_json, api_call = subreq.trigger(uri_path, lookup, 'sead')

        return_list.extend(resp_json)

    if params.get('order_id'):
        
        lookup = dict(order_id='in.(' + params.get('order_id') + ')')

        uri_path = ''.join([config.get('resource_api', 'sead'), 'taxa_tree_orders'])

        resp_json, api_call = subreq.trigger(uri_path, lookup, 'sead')

        return_list.extend(resp_json)

    # Now return whatever results we have collected. We have no way to return more than one API
    # call, so we just return the last one executed.
    
    return return_list, api_call



def occ_taxon_filter(taxon_name):
    """Given a taxon name, return a set of arguments that will select occurrences from that taxon."""
    
    or_list = list()
    
    # Split the name on commas, and then look up each item.
    
    for item in re.split("\s*,\s*", taxon_name):

        # Get a list of records that match the item name
        
        item_list, api_call = taxon_lookup(item)
        
        # For each record, add an appropriate entry to the or_list.

        for rec in item_list:

            # If the record contains a 'species' field, then it represents a species.
            
            if "species" in rec:
                expr = 'and(genus_name.eq.{},species.eq.{})'.format(rec.get('genus_name', 'select_nothing'),
                                                                    rec.get('species', 'select_nothing'))
                or_list.append(expr)

            # Otherwise, if it contains a 'genus_name' field, then it represents a genus.

            elif "genus_name" in rec:
                expr = 'genus_name.eq.' + rec.get('genus_name', 'select_nothing')
                or_list.append(expr)
            
            elif "family_name" in rec:
                expr = 'family_name.eq.' + rec.get('family_name', 'select_nothing')
                or_list.append(expr)

            elif "order_name" in rec:
                expr = 'order_name.eq.' + rec.get('order_name', 'select_nothing')
                or_list.append(expr)
    
    # If the list is empty, return something that will select nothing

    if len(or_list) == 0:
        return {'taxon_id': "eq.-1"}
    
    # Otherwise, return an or-expression
    
    else:
        return {'or': '(' + ','.join(or_list) + ')'}
