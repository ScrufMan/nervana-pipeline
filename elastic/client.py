from elasticsearch import Elasticsearch


def get_elastic_client():
    return Elasticsearch("http://localhost:9200")


def test_connection(es):
    # Check if connection can be established
    try:
        es.ping()
        return True
    except ConnectionError:
        return False
