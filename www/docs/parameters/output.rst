``output=json|csv``
    File format of the data return. Serialized JSON or tabular CSV. The meta-data block is a separate JSON object and thus is not included in the CSV file. The file name of the CSV file will include a shortend MD5 hash of the response data for identification purposes. Type: `str`. Default: "json"

.. warning::
    The web-based API `sandbox <http://earthlifeconsortium.org/api_v1/ui/>`_ hosted on this site **does not** support retrieval of CSV files. If you are using the sandbox to explore API parameters and wish to download a CSV file, copy the URL displayed under [Request URL] after running a query and paste it into the browser window appending ``&output=csv`` to the end.
