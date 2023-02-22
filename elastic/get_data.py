from elasticsearch import Elasticsearch


def search_by_value(value, index, client: Elasticsearch):
    query = {
        "match": {
            "value": value
        }
    }
    response = client.search(index=index, query=query)
    return response['hits']['hits']


def aggregate_by_field(field, index, client: Elasticsearch):
    agg = {
        "by_field": {

            "terms": {
                "size": 100,
                "field": "category.keyword"
            }
        }
    }
    response = client.search(index=index, aggs=agg)
    return response['aggregations']['by_field']['buckets']
