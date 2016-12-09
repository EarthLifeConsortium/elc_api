# EarthLife Consortium API (api_v1)

The ELC API is a composite api which generates and dispaches queries for the Neotoma and Paleobiology (PBDB)  
databases using a simplified, common resource retrival specification. Results are returned as aggregated JSON objects.

This project follows an "API first" development process where:
* The interface schema, complient with the OpenAPI (formally known as Swagger) version 2.0 specification, is first defined.
* Server stubs are generated from this definition.
* Routing is automatically handled by a Swagger complient interface library.
* Finally the server backend code is developed for each generated function.
* Changes to the API can be made in the schema during development and the changes pushed down through the code.
* A Swagger HTML5 based user interface is also generated for browsing the API documentation and testing the parameter calls.

This project is currently under development.  

## Contributers

Development team:
* [Julian Jenkins](http://github.com/jpjenk)
* [Simon Goring](http://github.com/SimonGoring)
* Mike Anderson

For more infomation about the EarthLife Consortium and it's members visit [EarthLifeConsortium.org](http://earthlifeconsortium.org).


## Technical Description

The API is being developed with the following modern open source tools:
* [Python 3](https://www.python.org)
* [Connexion](http://connexion.readthedocs.io/en/latest) (a Flask based HTTP routing framework that is complient with OpenAPI 2.0)
* [Flask](http://flask.pocoo.org) (a python micro web framework)
* [swagger-codegen](http://swagger.io/swagger-codegen) (a Java based templating engine which can use Flask+Connexion to generate the server)
* optionally, [swagger-edit](https://github.com/swagger-api/swagger-editor) (a Node.js based editor and validator for OpenAPI spec YAML files)
* [git](https://git-scm.com) (for version control) and [GitHub](http://github.com) (for repository hosting).
