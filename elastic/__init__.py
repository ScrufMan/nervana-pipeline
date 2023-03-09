from elastic.client import get_elastic_client, test_connection
from elastic.index_data import create_index_if_not_exists, index_file, index_entities
from elastic.get_data import get_all_datasets, find_entities, get_all_files
from elastic.aggregations import get_most_popular_by_type