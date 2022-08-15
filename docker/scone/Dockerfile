FROM registry.scontain.com:5050/sconecuratedimages/apps:python-3.7.3-alpine3.10-scone5.3.0

COPY _resources/app_encrypted /app

RUN mkdir /fspf
COPY _resources/fspf/fspf.pb /fspf/fspf.pb

COPY _resources/venv /venv

WORKDIR /app

CMD /venv/bin/python3 /app/app.py
