API Documentation
=================

.. note::
    These instructions cover the programatic usage of the Earth-Life Consortium RESTful API version 1. All requests will include /api_v1 in the base path and use the HTTP GET protocol.

An interactive web-based `sandbox <http://earthlifeconsortium.org/api_v1/ui/>`_ is available for exploring the API. The API can, of course be called directly using a browser, cURL or using your favorite HTTP library such as Requests. The generated query URL is available in the sandbox for copying and editing.

Occurrences
-----------

[description here]

**Base path**
    ``http://earthlifeconsortium.org/api_v1/occ?``

**Parameters**

.. include:: parameters/coordtype.rst

.. include:: parameters/includelower.rst

.. include:: parameters/limit.rst

.. include:: parameters/offset.rst

.. include:: parameters/output.rst

.. include:: parameters/show.rst

.. seealso::
    [example of this endpoint]

Locales
-------

[description here]

**Base path**
    ``http://earthlifeconsortium.org/api_v1/loc?``

**Parameters**

.. seealso::
    [example of this endpoint]

References
----------

[description here]

**Base path**
    ``http://earthlifeconsortium.org/api_v1/ref?``

**Parameters**

.. seealso::
    [example of this endpoint]

Taxa
----

[description here]

**Base path**
    ``http://earthlifeconsortium.org/api_v1/tax?``

**Parameters**

.. seealso::
    [example of this endpoint]

Miscellaneous endpoint
----------------------

ELC utilities ancillary to core data retrieval are collected in the ``misc`` controller and are accessible by appending the desired route to the base path.

Paleocoordinates
^^^^^^^^^^^^^^^^
Convert modern day cartesian coordinates into paleocoordinates using the GPlates [#]_ tectonics reconstruction model. Operationally this model is hosted by the Macrostrat Project [#]_ at the University of Wisconsin.

**Base path**
    ``http://earthlifeconsortium.org/api_v1/misc/paleocoords?``

**Parameters**

.. include:: parameters/coords.rst

.. warning::
    Due to restriction in GPlates, some coordinates are not rotatable. In this case, an error message will be returned.

.. include:: parameters/age.rst

.. include:: parameters/ageunits.rst

.. include:: examples/paleocoordinates.rst

Timebounds
^^^^^^^^^^
Return the oldest and youngest ages (bounds) spanning the specified range. Geologic ages are resolved according to ICS definitions [#]_.

**Base path**
    ``http://earthlifeconsortium.org/api_v1/misc/timebound?``

**Parameters**

.. include:: parameters/agerange.rst

.. include:: parameters/ageunits.rst

.. include:: examples/timebound.rst

Subtaxa
^^^^^^^
Return a list of all taxonomic names hierarchically below the specified taxon, optionaly including synonyms.

.. warning::
    This tool leverages the Paleobiology Database taxonomy system and, while comprehensive for many classes, may lack taxa for species that are not the historical focus of the database.

**Base path**
    ``http://earthlifeconsortium.org/api_v1/misc/subtaxa?``

**Parameters**

.. include:: parameters/taxon.rst

.. include:: parameters/synonyms.rst

.. seealso::
    [example of this endpoint]

Metadata
--------
All ``full`` or ``poll`` JSON responses include a metadata block which importantly indicates the URLs composed for the resource databases in addition to a timestamp, the age units and the type of geographic coordinates retrieved.

Error handling
--------------
API errors are reported according to IETF [#]_ standards including both server level 500 series and client level 400 series HTTP errors. As the ELC API leverages remote data service resources for much of it's functionality, bad requests to or lack of availability of these remote services may result in the propogation of a 400 level error as ELC is the client in this circumstance.

.. rubric:: Footnotes

.. [#]
    Wright, N., S. Zahirovic, R. D. Müller, and M. Seton (2013), Towards community-driven, open-access paleogeographic reconstructions: integrating open-access paleogeographic and paleobiology data with plate tectonics, Biogeosciences, 10, 1529-1541.

.. [#]
    Macrostrat public API: https://macrostrat.org/#api

.. [#]
    F. Gradstein, J. Ogg, and M. Schmitz, G. Ogg. 2012. The Geologic Time Scale 2012.

.. [#]
    Internet Engineering Task Force: Problem Details for HTTP APIs. https://tools.ietf.org/html/draft-ietf-appsawg-http-problem-00

