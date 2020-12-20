#
# Earthlifeconsortium API image
# 
# The image 'paleobiodb_earthlife_preload' can be built using the file 'Dockerfile-preload'.
# See that file for more information.

FROM paleomacro_earthlife_preload

EXPOSE 8008 8003

# To build this container with the proper timezone setting, use --build-arg TZ=xxx
# where xxx specifies the timezone in which the server is located, for example
# America/Chicago. The 'pbdb build' command will do this automatically. Without any
# argument the container will default to UTC, with no local time available. 

ARG TZ=Etc/UTC

RUN echo $TZ > /etc/timezone && \
    cp /usr/share/zoneinfo/$TZ /etc/localtime

COPY earthlife /usr/src/app

CMD ["uwsgi", "elc-api.uwsgi.ini"]

