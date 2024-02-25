import os

from elasticsearch import AsyncElasticsearch


def get_async_elastic_client() -> AsyncElasticsearch:
    host = os.environ.get("ELASTICSEARCH_URL")
    user = os.environ.get("ELASTIC_USER")
    password = os.environ.get("ELASTIC_PASSWORD")
    ca_cert = os.environ.get("ELASTICSEARCH_CACERT")

    if host is None or user is None or password is None or ca_cert is None:
        raise EnvironmentError(
            "ELASTICSEARCH_URL, ELASTIC_USER, ELASTIC_PASSWORD and ELASTICSEARCH_CACERT must be set in .env file")

    return AsyncElasticsearch(
        host,
        ca_certs=ca_cert,
        basic_auth=(user, password),
        timeout=200
    )


async def test_connection_async(es: AsyncElasticsearch):
    # Check if connection can be established
    can_connect = await es.ping()
    if not can_connect:
        raise ConnectionError()
