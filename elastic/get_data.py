from elasticsearch import Elasticsearch


def get_all_datasets(es: Elasticsearch):
    indices = es.indices.get_alias().keys()
    datasets = [index for index in indices if not index.startswith('.')]
    return datasets


def find_entities(es: Elasticsearch, dataset, search_conditions, page, page_size):
    search_query = {
        "bool": {
            "must": [
                {"match": {"type": "entity"}}
            ],
            "should": []
        }
    }

    for search_term, entity_type in search_conditions:
        match_query = {
            "bool": {
                "must": []
            }
        }

        if search_term != "*":
            match_query["bool"]["must"].append({"match": {"value": search_term}})
        if entity_type != "Všechny":
            match_query["bool"]["must"].append({"match": {"entity_type": entity_type}})

        # check query not empty
        if match_query["bool"]["must"]:
            search_query["bool"]["should"].append(match_query)

    index = dataset
    if index == "Všechny":
        index = "_all"

    start_index = (page - 1) * 10

    response = es.search(index=index, query=search_query, from_=start_index, size=page_size)
    return response["hits"]["total"]["value"], response['hits']['hits']


def get_all_files(es, dataset):
    index = dataset
    if index == "Všechny":
        index = "_all"

    query = {
        "match": {"type": "file"}
    }
    response = es.search(index=index, query=query)
    return response['hits']['hits']


def get_file(es, dataset, file_id):
    index = dataset

    try:
        res = es.get(index=index, id=file_id)
        return res["_source"]
    except Exception as e:
        print(f"Error retrieving document: {e}")


def aggregate_by_field(field, index, client: Elasticsearch):
    agg = {
        "by_field": {

            "terms": {
                "size": 100,
                "field": f"{field}.keyword"
            }
        }
    }
    response = client.search(index=index, aggs=agg)
    return response['aggregations']['by_field']['buckets']
