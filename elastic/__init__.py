from elastic.client import get_elastic_client, test_connection
from elastic.index_data import create_index_if_not_exists, index_file, index_entities