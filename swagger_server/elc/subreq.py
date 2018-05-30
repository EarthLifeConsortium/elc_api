"""Use the Requests HTTP library with pervasive error handling."""


def trigger(url_path, payload, db):
    """Primary safe requester method for external database resources."""
    import requests
    from ..elc import config

    try:
        resp = requests.get(url_path,
                            params=payload,
                            timeout=config.get('default', 'timeout'))
        resp.raise_for_status()

    except requests.exceptions.HTTPError as err:
        raise ValueError(resp.status_code, str(err.args[0]))

    except requests.exceptions.SSLError as err:
        raise ValueError(495, str(err.args[0]))

    except requests.exceptions.ConnectionError as err:
        raise ValueError(502, str(err.args[0]))

    except requests.exceptions.Timeout as err:
        raise ValueError(504, str(err.args[0]))

    except requests.exceptions.RequestException as err:
        raise ValueError(500, str(err.args[0]))

    # Check the Content-Type of the return and decode the JSON object

    if 'application/json' not in resp.headers.get('content-type'):
        msg = '{0:s} response is not of type application/json'.format(db)
        raise ValueError(417, msg)

    # Check that serialized JSON object is decodable

    try:
        resp_json = resp.json()

    except ValueError as err:
        msg = '{0:s} JSON decode error: {1:s}'.format(db, err)
        raise ValueError(500, msg)

    print(resp.url)

    return resp_json, resp.url
