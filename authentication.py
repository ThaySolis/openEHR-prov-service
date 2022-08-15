import flask_httpauth

from app_settings import AUTH_USERNAME, AUTH_PASSWORD

auth = flask_httpauth.HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    return username == AUTH_USERNAME and password == AUTH_PASSWORD
