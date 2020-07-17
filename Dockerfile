#
# Earthlifeconsortium API image
# 
# The image 'paleobiodb_earthlife_preload' can be built using the file 'Dockerfile-preload'.
# See that file for more information.

FROM paleomacro_earthlife_preload

COPY earthlife /usr/src/app

EXPOSE 8008

ENTRYPOINT ["python3"]

CMD ["-m", "swagger_server"]
