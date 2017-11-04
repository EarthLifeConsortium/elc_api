"""Read setting from config.yaml."""


def config(param, db_name):
    """
    Return the base URL for the subquery database.
    
    :arg param: Setting to return
    :arg db_name: Name of DB to retrieve for
    """
    import yaml

    with open('../../config.yaml') as f:
        data_map = yaml.safe_load(f)

    return data_map[param][db_name]
