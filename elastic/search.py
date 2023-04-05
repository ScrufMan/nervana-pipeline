from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from .helpers import dataset_to_indices
from entity_recognizer.post_processor import lemmatize_text


def handle_regexp(search_term):
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


def handle_exact(search_term):
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


def handle_normal(search_term):
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


def find_entities(es: Elasticsearch, dataset, search_terms, entity_types_list, page, page_size):
    indices = dataset_to_indices(es, dataset, file_indices=False)

    search = Search(using=es, index=indices)

    search_from = (page - 1) * page_size
    search = search[search_from:search_from + page_size]

    # Loop through search_terms and entity_types and create a search query for each term
    queries = []
    for search_term, entity_types in zip(search_terms, entity_types_list):
        if search_term.startswith('r:'):
            clause = handle_regexp(search_term)
        elif search_term.startswith('"') and search_term.endswith('"'):
            clause = handle_exact(search_term)
        else:
            clause = handle_normal(search_term)

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

    response = search.execute()

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
        res = es.get(index=index, id=file_id)["_source"]

        return res
    except Exception as e:
        print(f"Error retrieving document: {e}")
