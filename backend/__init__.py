from flask import Flask
from elastic import get_sync_elastic_client, test_connection_sync

try:
    es = get_sync_elastic_client()
    test_connection_sync(es)
except ConnectionError:
    print("Cannot connect to Elasticsearch")
    exit(1)

app = Flask(__name__)
app.config["SECRET_KEY"] = 'be05e096bbe940c8192912e4db46279e'

from backend import routes
