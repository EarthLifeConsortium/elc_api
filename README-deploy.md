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

Test the API using Flask's Werkzeug single threaded develoment server
```
python3 -m swagger_server
```

## Deployment
Run API concurrently across multiple logical cores using uWSGI
```
uwsgi --socket 127.0.0.1:8008 --callable app --file swagger_server/app.py --master -p 4 --threads 2 --stats 127.0.0.1:9009 --memory-report --wsgi-disable-file-wrapper
```
Note: `--protocol=http` is omitted becasuse NGINX can nativly speak the uWSGI protocol. These parameters are included in a config file so `uwsgi elc-api.ini` will also work. Daemonize the uWSGI stack with `-d /[path]/[logfile]`
If statistics and memory usage reporting is enabled, monitor workers with
```
uwsgitop 127.0.0.1:9009
```
To put the API behing a full webserver add a reverse proxy. NGINX supports the uWSGI native protocol so bind the port in nginx.conf with
```
location ^~ /api_v1 {
    include uwsgi_params;
    uwsgi_pass 127.0.0.1:8008;
}
```
The Sandbox UI can be customized to match the look and feel of the rest of the ELC site by symlinking the files in ./web_ui into the local installation of the Connexion library. Example:
```
ELC-logo-horz-M.png --> [path to connexion/vendor/swagger-ui/images/

index.html --> [path to connexion]/vendor/swagger-ui/
```

