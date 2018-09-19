``output=json|csv``
    File format of the data return. Serialized JSON or tabular CSV. The meta-data block is a separate JSON object and thus is not included in the CSV file. The file name of the CSV file will include a shortened MD5 hash of the response data for identification purposes. Type: `str`. Default: "json"
