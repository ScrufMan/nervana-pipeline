from typing import List

from elasticsearch import Elasticsearch


def get_all_datasets(es: Elasticsearch):
    indices = es.cat.indices(format="json")
    datasets = [(index["index"].split("-files")[0], index["index"].split("-files")[0]) for index in indices if
                not (index["index"].startswith(".") or index["index"].endswith("-entities"))]
    return datasets


def dataset_to_indices(es: Elasticsearch, dataset: str, file_indices: bool) -> List[str]:
    if file_indices:
        index_suffix = "-files"
    else:
        index_suffix = "-entities"

    if dataset == "all":
        # Get a list of all indices in the cluster
        indices = es.cat.indices(format="json")

        # Filter out the indices that end with suffix
        index = [index['index'] for index in indices if index['index'].endswith(index_suffix)]
    else:
        index = [f"{dataset}{index_suffix}"]

    return index
