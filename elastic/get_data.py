from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q


def get_all_datasets(es: Elasticsearch):
    indices = es.indices.get_alias().keys()
    datasets = [(index, index) for index in indices if not index.startswith('.')]
    return datasets


def find_entities(es: Elasticsearch, index, search_terms, entity_types, page, page_size):
    s = Search(using=es, index=index)

    search_from = (page - 1) * page_size
    s = s[search_from:search_from + page_size]

    # type of document must be entity
    document_type_query = Q('term', type="entity")

    # create a query to match documents with any of the given entity types
    entity_type_query = Q('terms', entity_type=entity_types)

    # create a query to match entites with any of the given values
    values_query = None
    for search_term in search_terms:
        if search_term.startswith('r:'):
            values_query_part = Q('query_string', query=search_term[2:], fuzziness='2', default_field='value')
        else:
            values_query_part = Q('fuzzy', value={'value': search_term, 'fuzziness': 'AUTO'})
        if values_query is None:
            values_query = values_query_part
        else:
            values_query |= values_query_part

    # combine the two queries with an "and" operator
    combined_query = document_type_query & entity_type_query & values_query

    # execute the search
    response = s.query(values_query).execute()

    return response


def get_all_files(es: Elasticsearch, index):
    s = Search(using=es, index=index)
    s = s[0:10000]
    response = s.query(Q("term", type="file")).execute()

    return response


def get_file(es, dataset, file_id):
    index = dataset

    try:
        res = es.get(index=index, id=file_id)
        return res["_source"]
    except Exception as e:
        print(f"Error retrieving document: {e}")
