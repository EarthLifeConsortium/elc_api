API Documentation
=================

.. note::
    These instructions cover the programmatic usage of the EarthLife Consortium RESTful API version 1. All requests will include /api_v1 in the base path and use the HTTP GET protocol.

An interactive web-based `sandbox <http://earthlifeconsortium.org/api_v1/ui/>`_ is available for exploring the API. The API can, of course be called directly using a browser, cURL or using your favorite HTTP library such as Requests. The generated query URL is available in the sandbox for copying and editing.

Occurrences
-----------
Occurrences are the individual instances of fossils in time and space. Occurrences of taxa can be specified at any taxonomic level bound by any units of time and spatial delimitation.

**Base path**
    ``http://earthlifeconsortium.org/api_v1/occ?``

**Parameters**

.. include:: parameters/taxon.rst
.. include:: parameters/taxonomichierarchy.rst
.. include:: parameters/bbox.rst
.. include:: parameters/agerange.rst
.. note::
    At a minimum, a ``taxon``, ``bbox`` or ``agerange`` parameter must be specified, however more than one of these may be used together to further constrain the query.'

.. include:: parameters/ageunits.rst
.. include:: parameters/coordtype.rst
.. include:: parameters/includelower.rst
.. include:: parameters/limit.rst
.. include:: parameters/offset.rst
.. include:: parameters/output.rst
.. include:: parameters/show.rst
.. include:: parameters/run.rst

**Examples**

.. include:: examples/occurrences.rst

Locales
-------
A locale is a cube of time-space delimited with geographic units and geologic time bounds.

**Base path**
    ``http://earthlifeconsortium.org/api_v1/loc?``

**Parameters**

.. include:: parameters/idlist.rst
.. note::
    ELC extended identifiers are both consumed and produced by various API routes. They consist of a three parameter, colon separated string which provides a universally unique identifier of a data resource object.

    Examples of ELC IDs for the locale (``/loc``) route would be ``neot:dst:998`` or ``pbdb:col:9191``. Because of the database specific names for locale data objects, neotoma will only use ``dst`` (dataset) and PBDB will only use ``col`` (collection).

.. include:: parameters/bbox.rst
.. include:: parameters/agerange.rst
.. note::
    If a list of ELC universal identifiers, ``idlist``, is not provided, then either ``bbox`` or ``agerange`` must be specified.

.. include:: parameters/ageunits.rst
.. include:: parameters/coordtype.rst
.. include:: parameters/limit.rst
.. include:: parameters/offset.rst
.. include:: parameters/output.rst
.. include:: parameters/show.rst
.. include:: parameters/run.rst

**Examples**

.. include:: examples/locales.rst

References
----------
References returns bibliographic information on the publications from which other data are derived.

**Base path**
    ``http://earthlifeconsortium.org/api_v1/ref?``

**Parameters**

.. include:: parameters/idlist.rst
.. note::
    Examples of valid ELC IDs for the references (``/ref``) route include ``pbdb:ref:100`` and ``neot:pub:234``. Database specific datatype names are again used in the ID construct, the ELC API route happens to be called ``/ref`` merely because there can only be one name.

.. include:: parameters/output_ref.rst
.. include:: parameters/show.rst
.. include:: parameters/run.rst

**Examples**

.. include:: examples/references.rst

Taxonomy
--------
Taxonomy returns the classification of a given taxon.

**Base path**
    ``http://earthlifeconsortium.org/api_v1/tax?``

**Parameters**

.. include:: parameters/taxon.rst
.. include:: parameters/taxonomichierarchy.rst
.. include:: parameters/idlist.rst
.. note::
    Either a taxon name or a list of ELC formatted taxonomic IDs must be provided. Examples of valid ELC IDs for the taxonomy (``/tax``) route include ``pbdb:txn:929`` and ``neot:txn:34``.

.. include:: parameters/includelower_false.rst
.. include:: parameters/output.rst
.. include:: parameters/show.rst
.. include:: parameters/run.rst

**Examples**

.. include:: examples/taxonomy.rst

Miscellaneous route
-------------------

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

**Examples**

.. include:: examples/paleocoordinates.rst

Timebounds
^^^^^^^^^^
Return the oldest and youngest ages (bounds) spanning the specified range. Geologic ages are resolved according to ICS definitions [#]_.

**Base path**
    ``http://earthlifeconsortium.org/api_v1/misc/timebound?``

**Parameters**

.. include:: parameters/agerange.rst
.. include:: parameters/ageunits.rst

**Examples**

.. include:: examples/timebound.rst

Subtaxa
^^^^^^^
Return a list of all taxonomic names hierarchically below the specified taxon, optionally including synonyms.

.. warning::
    This tool leverages the Paleobiology Database taxonomy system and, while comprehensive for many classes, may lack taxa for species that are not the historical focus of the database.

**Base path**
    ``http://earthlifeconsortium.org/api_v1/misc/subtaxa?``

**Parameters**

.. include:: parameters/taxon.rst
.. include:: parameters/synonyms.rst

**Examples**

.. include:: examples/subtaxa.rst

Mobile
^^^^^^
A custom route designed to return a combination of occurrence data with associated taxonomic and select environmental details. The response is nested JSON with a highly compact vocabulary.

**Base path**
    ``http://earthlifeconsortium.org/api_v1/misc/mobile?``

**Parameters**

.. include:: parameters/taxon.rst
.. include:: parameters/bbox.rst

**Compact vocabulary**

=== ==========================
src ELC formatted unique occurrence ID
=== ==========================

|

=== ==========================
loc Location parameter block
=== ==========================
age Early, Late age (Ma)
crd Coordinates (GeoJSON)
pla Place (county/district, state/province, country)
ste Site/Collection description
=== ==========================

| 

=== ==========================
org Organism parameter block
=== ==========================
img Phylopic image URI
itv Early, Late geologic existence interval
nam Common name
sts Status of modern existence 
txn Taxonomic name
=== ==========================

| 

=== ==========================
eco Ecology parameter block
=== ==========================
dte Diet/Feeding mode
env Environmental description
grp Ecological/Taxonomic grouping/env basis
hab Life habitat, grouping or depth
mot Motility and/or attachment
ont Ontology
rep Mode of reproduction
typ Collection/Dataset type
vis Vision capability
=== ==========================

**Examples**

.. include:: examples/mobile.rst

`Metadata`
    All ``full`` or ``poll`` JSON responses include a metadata block which importantly indicates the URLs composed for the resource databases in addition to a timestamp, the age units and the type of geographic coordinates retrieved. If desired, the subquery URL may be used to delve deeper into each individual database.

`Error handling`
    API errors are reported according to IETF [#]_ standards including both server level 500 series and client level 400 series HTTP errors. As the ELC API leverages remote data service resources for much of it's functionality, bad requests to or lack of availability of these remote services may result in the propogation of a 400 level error as ELC is the client in this circumstance.

.. rubric:: Footnotes

.. [#]
    BibJSON: Representing bibliographic metadata in JSON. http://okfnlabs.org/bibjson/

.. [#]
    Wright, N., S. Zahirovic, R. D. Müller, and M. Seton (2013), Towards community-driven, open-access paleogeographic reconstructions: integrating open-access paleogeographic and paleobiology data with plate tectonics, Biogeosciences, 10, 1529-1541. DOI: `10.5194/bg-10-1529-2013 <https://www.researchgate.net/publication/235789001_Towards_community-driven_paleogeographic_reconstructions_Integrating_open-access_paleogeographic_and_paleobiology_data_with_plate_tectonics>`_

.. [#]
    Macrostrat public API. https://macrostrat.org/#api

.. [#]
    Gradstein, F. M., J. G. Ogg, M. D. Schmitz, and G. M. Ogg. 2012. `A Geologic Time Scale 2012 <https://www.elsevier.com/books/the-geologic-time-scale-2012/gradstein/978-0-444-59425-9>`_, Volume 2. Elsevier, Amsterdam, 1144 pp.

.. [#]
    Internet Engineering Task Force: Problem Details for HTTP APIs. https://tools.ietf.org/html/draft-ietf-appsawg-http-problem-00

