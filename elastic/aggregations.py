from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from elasticsearch_dsl.aggs import Terms, A

from .helpers import dataset_to_indices


def get_top_files_field_values(es: Elasticsearch, datset, field):
    indices = dataset_to_indices(es, datset)

    # create a Search object for the "files" index
    s = Search(using=es, index=indices[0])

    # define the aggregation
    aggregation = A("terms", field=field, size=5)

    # add the aggregation to the search object
    s.aggs.bucket("file_types", aggregation)

    # execute the search and retrieve the aggregation results
    print(s.to_dict())
    response = s.execute()

    result = {f"{bucket.key}": bucket.doc_count for bucket in response.aggregations.file_types.buckets}

    return result
    # print the aggregation results
    for bucket in response.aggregations.file_types.buckets:
        print(f"{bucket.key}: {bucket.doc_count} ({bucket.doc_count / response.hits.total.value:.2%})")


def get_top_values_for_field(es: Elasticsearch, index, type_field_name, entity_type, field_name):
    s = Search(using=es, index=index)

    kwargs = {type_field_name: entity_type}
    # Add a filter to only include documents with the specified entity_type
    s = s.filter(Q('term', **kwargs))

    # Define the Terms aggregation to get the top 5 values for the field
    aggs = Terms(field=field_name, size=5)

    # Add the aggregation to the search
    s.aggs.bucket("top_values", aggs)

    # Execute the search
    response = s.execute()

    # Process the aggregation results
    total_docs = response.hits.total.value
    top_values = {}
    for bucket in response.aggregations.top_values.buckets:
        value = bucket.key
        count = bucket.doc_count
        percentage = round((count / total_docs) * 100, 2)
        top_values[value] = percentage

    return top_values
