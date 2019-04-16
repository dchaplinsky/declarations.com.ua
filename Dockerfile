FROM python:3.6.8-alpine3.9

ARG root=/app
ARG R_BASE_VERSION=3.5.2

LABEL kind=app

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=${root} PREFIX=${root} \
		STATIC_ROOT=/static MEDIA_ROOT=/media \
		STATIC_ROOT_SOURCE=/static-source \
    NACP_DECLARATIONS_PATH=/import \
    DRAGNET_EXPORT_PATH=${root}/dragnet/data/export DRAGNET_IMPORT_PATH=${root}/dragnet/data/import \
    EXPORT_TMP=/export-tmp \
    APP_NAME="declarations_site.wsgi:application" APP_WORKERS="2"

WORKDIR ${root}

RUN /usr/sbin/adduser -D -h ${root} app

COPY requirements.txt ${root}/requirements.txt
COPY dragnet/utils/requirements.txt ${root}/dragnet/utils/requirements.txt

RUN apk add --no-cache su-exec postgresql-libs libjpeg libxml2 libstdc++ binutils libffi libxslt \
    && apk add --no-cache --virtual .build-deps jpeg-dev zlib-dev postgresql-dev build-base \
        libffi-dev libxml2-dev libxslt-dev \
    && PREFIX=/usr/local pip install cython -r ${root}/requirements.txt \
    # do not mix this with above
    && PREFIX=/usr/local pip install -r ${root}/dragnet/utils/requirements.txt \
    && runDeps="$( \
      scanelf --needed --nobanner --format '%n#p' --recursive /usr/local \
        | tr ',' '\n' \
        | sort -u \
        | awk 'system("[ -e /usr/local/lib" $1 " ]") == 0 { next } { print "so:" $1 }' \
    )" \
      apk add --no-cache --virtual .app-rundeps $runDeps \
    && apk del .build-deps \
    && rm -rf /root/.cache

RUN apk add --no-cache --repository http://dl-3.alpinelinux.org/alpine/edge/testing/ lbzip2

COPY docker-entrypoint.sh /usr/local/bin/

ARG version
RUN [ "x${version}" = "x" ] && echo 'build-arg "version" is is missing' && exit 1 || exit 0
ENV VERSION=${version}

COPY declarations_site ${root}/declarations_site
COPY dragnet ${root}/dragnet

ENV PYTHONPATH=${root}/declarations_site

COPY aggregated_migrated.json.tmpl /aggregated_migrated.json.tmpl

RUN mkdir -p ${STATIC_ROOT} ${STATIC_ROOT_SOURCE} ${MEDIA_ROOT} \
             ${NACP_DECLARATIONS_PATH} \
             ${DRAGNET_EXPORT_PATH} ${DRAGNET_IMPORT_PATH} \
             ${EXPORT_TMP} \
    && apk add --no-cache ruby npm curl \
    && apk add --no-cache --virtual .static-build-deps ruby-dev build-base ruby-rdoc gettext \
    && gem install sass \
    && envsubst < /aggregated_migrated.json.tmpl > ${root}/dragnet/data/profiles/aggregated_migrated.json \
    && apk del .static-build-deps \
    && npm config set unsafe-perm true \
    && npm install -g uglify-js \
    && python -m compileall ${root} \
    && PATH=${PATH}:${root}/bin \
       STATIC_ROOT=${STATIC_ROOT_SOURCE} \
       python ${root}/declarations_site/manage.py collectstatic


ENTRYPOINT [ "docker-entrypoint.sh" ]

VOLUME [ "${STATIC_ROOT}", "${MEDIA_ROOT}", \
         "${NACP_DECLARATIONS_PATH}", \
         "${DRAGNET_EXPORT_PATH}", "${DRAGNET_IMPORT_PATH}", \
         "${EXPORT_TMP}" ]

EXPOSE 8000

CMD [ "gunicorn" ]
