from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q


def get_all_datasets(es: Elasticsearch):
    indices = es.cat.indices(format="json")
    datasets = [(index["index"].split("-files")[0], index["index"].split("-files")[0]) for index in indices if
                not (index["index"].startswith(".") or index["index"].endswith("-entities"))]
    return datasets


def find_entities(es: Elasticsearch, dataset, search_terms, entity_types, page, page_size):
    if dataset == "_all":
        # Get a list of all indices in the cluster
        indices = es.cat.indices(format="json")

        # Filter out the indices that end with "-entities"
        index = [index["index"] for index in indices if index["index"].endswith("-entities")]
    else:
        index = f"{dataset}-entities"

    s = Search(using=es, index=index)

    search_from = (page - 1) * page_size
    s = s[search_from:search_from + page_size]

    # create a query to match documents with any of the given entity types
    entity_type_query = Q('terms', entity_type=entity_types)

    # create a query to match entites with any of the given values
    values_query = None
    for search_term in search_terms:
        if search_term.startswith('r:'):
            values_query_part = Q('query_string', query=search_term[2:], fuzziness='AUTO', default_field='value')
        else:
            values_query_part = Q('fuzzy', lemmatized={'value': search_term, 'fuzziness': 'AUTO'})
        if values_query is None:
            values_query = values_query_part
        else:
            values_query |= values_query_part

    # combine the two queries with an "and" operator
    combined_query = entity_type_query & values_query

    # execute the search
    response = s.query(values_query).execute()

    return response


def get_all_files(es: Elasticsearch, dataset):
    if dataset == "_all":
        # Get a list of all indices in the cluster
        indices = es.cat.indices(format="json")

        # Filter out the indices that end with "-entities"
        index = [index["index"] for index in indices if index["index"].endswith("-files")]
    else:
        index = f"{dataset}-files"

    s = Search(using=es, index=index)
    s = s[0:10000]
    response = s.query(Q("match_all")).execute()

    return response


def get_file(es, dataset, file_id):
    if dataset == "_all":
        # Get a list of all indices in the cluster
        indices = es.cat.indices(format="json")

        # Filter out the indices that end with "-entities"
        index = [index["index"] for index in indices if index["index"].endswith("-files")]
    else:
        index = f"{dataset}-entities"

    try:
        res = es.get(index=index, id=file_id)
        return res["_source"]
    except Exception as e:
        print(f"Error retrieving document: {e}")
