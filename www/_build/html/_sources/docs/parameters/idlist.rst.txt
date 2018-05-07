``idlist=database:datatype:id_number,[...]``
    Comma separated list of database specific ID numbers in the ELC extended format:
        * ``database``: Subquery database name. Only first four characters are read so, for example, either "neot" or "neotoma" may be used
        * ``datatype``: Short name for the data object to be returned. This is relative to both the database and the endpoint in question
        * ``id_number``: A database specific numerical identifier
