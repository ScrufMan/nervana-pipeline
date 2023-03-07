from flask import Flask
from elastic import get_elastic_client

es = get_elastic_client()
app = Flask(__name__)
app.config["SECRET_KEY"] = 'be05e096bbe940c8192912e4db46279e'

from backend import routes
