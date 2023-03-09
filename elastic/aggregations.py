from elasticsearch import Elasticsearch


def get_most_popular_by_type(es: Elasticsearch, field, dataset):
    index = dataset
    if index == "Všechny":
        index = "_all"

    query = {
        "aggs": {
            "categories": {
                "terms": {
                    "field": f"{field}.keyword",
                    "size": 5
                }
            }
        },
        "size": 0
    }

    # Execute the query and get the results
    result = es.search(index=index, body=query)
    total_count = result["hits"]["total"]["value"]
    # Extract the category buckets from the results
    buckets = result["aggregations"]["categories"]["buckets"]

    for bucket in buckets:
        category = bucket["key"]
        count = bucket["doc_count"]
        percentage_occurrence = count / total_count * 100