from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from .helpers import dataset_to_indices


def find_entities(es: Elasticsearch, dataset, search_terms, entity_types, page, page_size):
    indices = dataset_to_indices(es, dataset, file_indices=False)

    s = Search(using=es, index=indices)

    search_from = (page - 1) * page_size
    s = s[search_from:search_from + page_size]

    # create a query to match documents with any of the given entity types
    entity_type_query = Q('terms', entity_type=entity_types)

    # create a query to match entites with any of the given values
    values_query = None
    for search_term in search_terms:
        if search_term.startswith('"') and search_term.endswith('"'):
            values_query_part = Q('match', value=search_term[1:-1])
        elif search_term.startswith('r:'):
            values_query_part = Q('query_string', query=search_term[2:], fuzziness='AUTO', default_field='value')
        else:
            values_query_part = Q('fuzzy',
                                  lemmatized={'value': search_term, 'fuzziness': 'AUTO', 'transpositions': True})

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
    indices = dataset_to_indices(es, dataset, file_indices=True)

    s = Search(using=es, index=indices)
    s = s[0:10000]
    response = s.query(Q("match_all")).execute()

    return response


def get_file(es, dataset, file_id):
    index = f"{dataset}-files"

    try:
        res = es.get(index=index, id=file_id)

        return res
    except Exception as e:
        print(f"Error retrieving document: {e}")
