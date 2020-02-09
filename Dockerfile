#
# Earthlifeconsortium API

FROM python:3-alpine AS paleobiodb_earthlife_preload

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY earthlife/requirements.txt /usr/src/app/

RUN pip3 install --no-cache-dir -r requirements.txt

FROM paleobiodb_earthlife_preload

COPY earthlife /usr/src/app

EXPOSE 8008

ENTRYPOINT ["python3"]

CMD ["-m", "swagger_server"]
