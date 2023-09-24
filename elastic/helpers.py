from elasticsearch import Elasticsearch


def get_all_datasets(es: Elasticsearch):
    indices = es.cat.indices(format="json")
    datasets = [(index["index"], index["index"]) for index in indices if
                not index["index"].startswith(".")]
    return datasets


def get_stored_fileformats(es: Elasticsearch):
    indices = dataset_to_indices(es, "all")
    result = es.search(index=indices, body={"aggs": {"formats": {"terms": {"field": "format"}}}})
    formats = [bucket["key"] for bucket in result["aggregations"]["formats"]["buckets"]]
    return formats


def get_stored_file_languages(es: Elasticsearch):
    indices = dataset_to_indices(es, "all")
    result = es.search(index=indices, body={"aggs": {"languages": {"terms": {"field": "language"}}}})
    languages = [bucket["key"] for bucket in result["aggregations"]["languages"]["buckets"]]
    return languages


def dataset_to_indices(es: Elasticsearch, dataset: str) -> list[str]:
    if dataset == "all":
        # Get a list of all indices in the cluster
        indices = es.cat.indices(format="json")
        indices = [index['index'] for index in indices if not (index['index'].startswith('.'))]
    else:
        indices = [dataset]

    return indices
