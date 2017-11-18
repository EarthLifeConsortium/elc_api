"""Common output generators functions for the API controllers."""


def type_json(data):
    """Format data as a JSON return."""
    fmt_obj = dict()

    for key in data:
        fmt_obj.update({key: data[key]})

    return fmt_obj


def type_csv(data):
    """Format data as a tabular CSV file."""
    fmt_obj = dict()

    return fmt_obj


def type_bibjson(data):
    fmt_obj = dict()

    return fmt_obj


def type_ris(data):
    fmt_obj = dict()

    return fmt_obj


def type_itis(data):

    return fmt_obj


def type_plain(data):
    """Return a list of strings as plain text."""
    from flask import Response

    return Response('\n'.join(data),
                    content_type='text/plain; charset=utf-8')
