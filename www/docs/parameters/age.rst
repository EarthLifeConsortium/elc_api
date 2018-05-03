`age=value`
    Required. Historical age of desired paleocoodinates where `value` is an integer from 1 to 580 Ma or a named geologic age. If a numerical age is specified, it may be in the units of the ageunits parameter. Type: ``str`` or ``int``

.. note::
    The Ma 580 limit **only** applies to the paleocoordinates calculation. `agerange` searches in other API routes refer to the actual ages of the paleobiological records and have no limits.
