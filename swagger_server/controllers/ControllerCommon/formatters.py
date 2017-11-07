"""Common output generators functions for the API controllers."""


def type_json(obj):
    """Format the objurrence data as a JSON return."""
    fmt_obj = dict()

    for key in obj:
        fmt_obj.update({key: obj[key]})

    return fmt_obj


def type_csv(obj):
    """Format the objurrence data as a tabular CSV file."""
    fmt_obj = dict()

    return fmt_obj


def type_bibjson(obj):
    fmt_obj = dict()

    return fmt_obj


def type_ris(ojb):
    fmt_obj = dict()

    return fmt_obj


def type_itis(obj):

    return fmt_obj
