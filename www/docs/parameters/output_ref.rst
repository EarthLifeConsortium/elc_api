``output=json|csv|bibjson|ris``
    File format of the data return. Serialized JSON, structured BibJSON, tabular CSV or RIS interchange formats. The meta-data block is a separate JSON object and thus is not included in the CSV file. The file name of the CSV file will include a shortend MD5 hash of the response data for identification purposes. Type: `str`. Default: "bibjson"
