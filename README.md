# EarthLife Consortium API (api_v1)

The ELC API is a composite api which generates and dispaches queries for the Neotoma and Paleobiology (PBDB)  
databases using a simplified, common resource retrival specification. Results are returned as aggregated JSON objects.

This project is currently under development 

## Contributers
* [Julian Jenkins](http://github.com/jpjenk)  
* [Simon Goring](http://github.com/SimonGoring)  

## Technical Description

This project follows an "API first" development process where:
* The interface schema, complient with the OpenAPI (aka. Swagger) version 2 specification, is first defined.
* Server stubs are generated from this definition.
* Routing is automatically handled by a Swagger complient interface library.
* Finally the server backend code is developed for each generated function.
* Changes to the API can be made in the schema during development and the changes pushed down through the code.
* A Swagger HTML5 based user interface is also generated for browsing the API documentation and testing the parameter calls.
