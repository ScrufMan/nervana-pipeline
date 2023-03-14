from elasticsearch import Elasticsearch

SEARCH_TO_UNIVERSAL = {
    "Osoba": "person",
    "Datum": "datetime",
    "Lokace": "location",
    "Číslo účtu": "bank_account",
    "BTC adresa": "btc_adress",
    "Telefonní číslo": "phone",
    "Emailová adresa": "email",
    "Internetový odkaz": "link",
    "Organizace": "organization"
}


def get_all_datasets(es: Elasticsearch):
    indices = es.indices.get_alias().keys()
    datasets = [index for index in indices if not index.startswith('.')]
    return datasets


def find_entities(es: Elasticsearch, term, dataset, entity_type, page, page_size):
    query = {
        "bool": {
            "must": [
                {"match": {"type": "entity"}}
            ]
        }
    }

    if term != "*":
        query["bool"]["must"].append({"match": {"value": term}})

    if entity_type != "Všechny":
        query["bool"]["must"].append({"match": {"entity_type": SEARCH_TO_UNIVERSAL[entity_type]}})

    index = dataset
    if index == "Všechny":
        index = "_all"

    start_index = (page - 1) * 10

    response = es.search(index=index, query=query, from_=start_index, size=page_size)
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
                "field": "category.keyword"
            }
        }
    }
    response = client.search(index=index, aggs=agg)
    return response['aggregations']['by_field']['buckets']
