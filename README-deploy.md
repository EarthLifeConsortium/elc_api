# EarthLife Consortium API production deployment


This deployment utilizes:
* NGINX as the gateway webserver and reverse proxy
* uWSGI as the preforking application server
* A POSIX complient Unix-like underlying OS


## Installation
Install API with
```
git clone https://github.com/EarthLifeConsortium/elc_api.git
pip3 install -r requirements.txt
```
Install uWSGI
```
pip3 install uwsgi
```
Use the system installer (brew, apt-get, rpm, port etc.) to build NGINX and, optionally, swagger-codegen


## Development
Develop and debug OpenAPI (aka Swagger) definition with swagger-editor
```
git clone https://github.com/swagger-api/swagger-editor.git
npm start
```

Build initial server stubs with swagger-codegen
```
swagger-codegen generate -i ./swagger.yaml -l python-flask -o [your path]/elc_api
```

Test the API using Flask's Werkzeug single threadded develoment server
```
python3 -m swagger_server
```

## Deployment
Run API concurrently across N logical cores using uWSGI
```
uwsgi --socket 127.0.0.1:8008 --protocol=http --callable app --file swagger_server/app.py --master -p 4 --stats 127.0.0.1:8181
```
Monitor workers with
```
uwsgitop 127.0.0.1:8118
```
To put the API behing a full webserver add a reverse proxy. NGINX supports the uWSGI native protocol so bind the port in nginx.conf with
```
location / {
    include uwsgi_params;
    uwsgi_pass 127.0.0.1:8008;
}
```
