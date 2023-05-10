from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from .helpers import dataset_to_indices
from entity_recognizer.post_processor import lemmatize_text


def create_regexp_query(search_term):
    return [
        {
            "regexp": {
                "value.keyword": search_term[2:]
            }
        },
        {
            "regexp": {
                "lemmatized.keyword": search_term[2:]
            }
        }
    ]


def create_exact_match_query(search_term):
    exact_term = search_term[1:-1]
    return [
        {
            "term": {
                "value.keyword": exact_term
            }
        },
        {
            "term": {
                "lemmatized.keyword": exact_term
            }
        }
    ]


def create_normal_query(search_term):
    if search_term == "*":
        return [
            {
                "match_all": {}
            }
        ]

    lemmatized_search_term = lemmatize_text(search_term)

    return [
        {
            "function_score": {
                "query": {
                    "multi_match": {
                        "query": search_term,
                        "fields": ["value", "value.english"]
                    }
                },
                "boost": 2
            }
        },
        {
            "function_score": {
                "query": {
                    "multi_match": {
                        "query": lemmatized_search_term,
                        "fields": ["lemmatized", "lemmatized.english"]
                    }
                },
                "boost": 2
            }
        },
        {
            "fuzzy": {
                "value": {
                    "value": search_term,
                    "fuzziness": "AUTO"
                }
            }
        },
        {
            "fuzzy": {
                "lemmatized": {
                    "value": lemmatized_search_term,
                    "fuzziness": "AUTO"
                }
            }
        },
        {
            "fuzzy": {
                "value.english": {
                    "value": search_term,
                    "fuzziness": "AUTO"
                }
            }
        },
        {
            "fuzzy": {
                "lemmatized.english": {
                    "value": lemmatized_search_term,
                    "fuzziness": "AUTO"
                }
            }
        }
    ]


def add_entities_query_to_search(search, search_terms, entity_types_list):
    # Loop through search_terms and entity_types and create a search query for each term
    queries = []
    for search_term, entity_types in zip(search_terms, entity_types_list):
        if search_term.startswith('r:'):
            clause = create_regexp_query(search_term)
        elif search_term.startswith('"') and search_term.endswith('"'):
            clause = create_exact_match_query(search_term)
        else:
            clause = create_normal_query(search_term)

        query = Q(
            "bool",
            should=clause,
            filter=[
                {
                    "terms": {
                        "entity_type": entity_types
                    }
                }
            ],
            minimum_should_match=1
        )

        queries.append(query)

    search = search.query(
        "bool",
        should=queries,
        minimum_should_match=1
    )

    return search


def find_entities_with_limit(es: Elasticsearch, dataset, search_terms, entity_types_list, page, page_size):
    indices = dataset_to_indices(es, dataset)

    search = Search(using=es, index=indices)

    search_from = (page - 1) * page_size
    search = search[search_from:search_from + page_size]

    search = add_entities_query_to_search(search, search_terms, entity_types_list)

    response = search.execute()

    return response


def find_all_entities(es: Elasticsearch, dataset, search_terms, entity_types_list):
    indices = dataset_to_indices(es, dataset, file_indices=False)

    search = Search(using=es, index=indices)

    search = add_entities_query_to_search(search, search_terms, entity_types_list)

    response = search.scan()

    return response


def get_all_files(es: Elasticsearch, dataset):
    indices = dataset_to_indices(es, dataset, file_indices=True)

    s = Search(using=es, index=indices)
    response = s.query(Q("match_all")).scan()

    return response


def get_filepaths_by_ids(es: Elasticsearch, files):
    paths = []
    for index, file_id in files:
        try:
            res = es.get(index=index, id=file_id)
            paths.append(res["_source"]["path"])
        except Exception as e:
            print(f"Error retrieving file from elastic: {e}")

    return paths


def get_file(es, dataset, file_id):
    index = f"{dataset}-files"
    try:
        res = es.get(index=index, id=file_id)["_source"]
        return res
    except Exception as e:
        print(f"Error retrieving file from elastic: {e}")
        return None
