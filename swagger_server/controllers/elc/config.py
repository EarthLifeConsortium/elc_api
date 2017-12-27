"""Read settings from config.yaml."""


def read_file(filename):
    """Local file reader function."""
    import yaml

    with open(filename) as f:
        return yaml.safe_load(f)


def get(group, param):
    """
    Return specified configurationa parameters.

    :arg param: Setting to return
    :type param: str
    :arg db_name: Name of DB to retrieve for
    :type db_name: str
    """
    data_map = read_file('config.yaml')

    return data_map[group][param]


def db_list():
    """Return names of all external queryable database resources."""
    data_map = read_file('config.yaml')

    return data_map['resource_api'].keys()
