# OpenEHR PROV service

> This project is part of Thayse Marques Solis' masters project, yet to be released.

This project is an implementation of a web service which consumes data from openEHR and demographic APIs and renders the change history of versioned objects (`EHR_STATUS`, `COMPOSITION` and `patient` objects) according to the PROV standard. This web service is compliant to the 'direct HTTP query service' specification whch is part of the PROV-AQ standard.

## Running locally

In order to run this service locally, you must first create the Python virtual environment:

```bash
python3 -m venv venv
```

Then, after activating the virtual environment, you must install all requirements.

```bash
pip install -r requirements.txt
```

Finally, you may run the Python application:

```bash
python app.py
```

## Environment variables

In order to run this application, the environment variables described in this section must be set.

> The `.env` file is provided with sample values for these variables.

### PROV API settings

- `PLAIN_HTTP`: if `yes`, the server will run in HTTP mode, else it will run in HTTPS mode.
- `SERVER_PORT`: the port that will receive incoming HTTP requests.
- `AUTH_USERNAME`: username that must be used to access this service using HTTP basic authentication.
- `AUTH_PASSWORD`: password that must be used to access this service using HTTP basic authentication.
- `INCLUDE_USAGE_STATISTICS`: if `yes`, the server will collect usage statisticas and provide an additional route `/usage_statistics` to get usage statistics.
- `USAGE_STATISTICS_MAX_SAMPLES`: the maximum number of timing samples collected for the usage statistics.

### OpenEHR API access settings

- `PUBLIC_OPENEHR_API_BASE_URI`: the public URI used to access the openEHR API - this is the base URI that the clients will use to refer to openEHR resources.
- `PRIVATE_OPENEHR_API_BASE_URI`: the private URI used to access the openEHR API - this is the base URI that this service will use access openEHR resources.
- `OPENEHR_API_AUTH_USERNAME`: username that will be used to access the openEHR API using HTTP basic authentication.
- `OPENEHR_API_AUTH_PASSWORD`: password that will be used to access the openEHR API using HTTP basic authentication.
- `VALIDATE_OPENEHR_API_CERTIFICATE`: if `yes`, the SSL certificate of the openEHR API will be validated (this setting has no effect if the openEHR API uses HTTP).
- `USE_CUSTOM_OPENEHR_API_CA_CERTIFICATE`: if `yes`, the root CA certificate of the certification chain of the openEHR API will be validated based on the file `other_certificates/openehr_api_ca_certificate.pem`.

### Demographic API access settings

- `PUBLIC_DEMOGRAPHIC_BASE_URI`: the public URI used to access the demographic API - this is the base URI that the clients will use to refer to demographic resources.
- `PRIVATE_DEMOGRAPHIC_API_BASE_URI`: the private URI used to access the demographic API - this is the base URI that this service will use access demographic resources.
- `DEMOGRAPHIC_API_AUTH_USERNAME`: username that will be used to access the demographic API using HTTP basic authentication.
- `DEMOGRAPHIC_API_AUTH_PASSWORD`: password that will be used to access the demographic API using HTTP basic authentication.
- `VALIDATE_DEMOGRAPHIC_API_CERTIFICATE`: if `yes`, the SSL certificate of the demographic API will be validated (this setting has no effect if the demographic API uses HTTP).
- `USE_CUSTOM_DEMOGRAPHIC_API_CA_CERTIFICATE`: if `yes`, the root CA certificate of the certification chain of the demographic API will be validated based on the file `other_certificates/demographic_api_ca_certificate.pem`.

