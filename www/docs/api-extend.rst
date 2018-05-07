Extending the API
=================

The strength of the ELC API grows with the addition of other paleoecological and biological databases. Research groups and developers are strongly encouraged to fork the ELC framework and follow the steps described below to add a new database as an ELC resource.

The ELC API is denoted by major version within the base path itself and all sub-versions of the API will not break parameter, route or response compatibility. If, in the future, the API is expanded or modified in such a was that this compatability in untenable, a new major version will be launched. Earlier versions will, however, remain available.

.. note::
    This section contains technical information relevant to a developer audience.

Handlers
--------
The majority of code required to support each resource database is contained in a file named ``handlers/[database_name].py``. As every subquery resource will return data differing in structure and tag vocabulary, a custom "handler" is required to process and map these returns to the common ELC dictionaries.

It is suggested that one of the existing handler be used as a template, paying close attention to the ``data.update()`` statements as these load the ELC response object. These fields are all required. If a parameter can not be returned by the new resource database, ``data.update(UnretrievableParamName=None)`` statements must be included. This will insert a `Null` into the JSON response and a blank field in a CSV download.

Inline modifications
--------------------
A few locations in the primary source code require additional augmentation to support a new resource database. These are all clearly maked with the comment::

# NEW RESOURCE: [information about the code block to be added]

In some cases addition code may be optional but the source files containing new database hooks are::

- handlers/router.py
- elc/aux.py
- elc/params.py (3 locations)
- elc/taxa.py
- elc/ages.py

Configuration file
------------------
Requisite information must be added to each data block in the ``config.yaml`` file. If a particular query is not possible with the database to be added, leave it's endpoint field blank and the ELC API will omit this database when calling that route.
