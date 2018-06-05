"""Read settings from config.yaml."""


def read_file(filename):
    """Local file reader function."""
    import yaml

    with open(filename) as f:
        return yaml.safe_load(f)


def get(group, param):
    """
    Return specified configuration parameters.

    :arg group: Setting category
    :type group: str
    :arg param: Setting name
    :type param: str
    """
    data_map = read_file('config.yaml')

    return data_map[group][param]


def db_list():
    """Return names of all external queryable database resources."""
    data_map = read_file('config.yaml')

    return data_map['run_list']
