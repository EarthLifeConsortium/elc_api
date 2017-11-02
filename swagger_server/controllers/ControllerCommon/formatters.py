"""Common output generators functions for the API controllers."""

def format_json(occ):
    """Format the occurrence data as a JSON return."""
    fmt_occ = dict()

    for key in occ:
        fmt_occ.update({key: occ[key]})

    return fmt_occ


def format_csv(occ):
    """Format the occurrence data as a tabular CSV file."""
    fmt_occ = dict()

    return fmt_occ
