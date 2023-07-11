from flask import render_template

from backend import app, es
from backend.forms import EntityTypeForm


@app.route("/")
@app.route("/stats")
def stats():
    entity_type_to_czech = {
        "person": "Osoba",
        "datetime": "Datum",
        "location": "Lokace",
        "bank_account": "Číslo účtu",
        "btc_adress": "BTC adresa",
        "phone": "Telefonní číslo",
        "email": "Emailová adresa",
        "link": "Internetový odkaz",
        "organization": "Organizace",
        "document": "Dokument",
        "product": "Produkt",
        "artifact": "Artefakt"
    }

    from elasticsearch_dsl import Search

    form = EntityTypeForm()

    search = Search(using=es, index="testovaci_dataset")

    # Aggregations for graph data
    search.aggs.bucket("file_formats", "terms", field="format")
    search.aggs.bucket("entity_types", "terms", field="entity_type")
    search.aggs.bucket("most_common_values", "terms", field="lemmatized.keyword")

    # Define the aggregation
    search.aggs.bucket(
        'files_with_most_entities',  # The name of the aggregation
        'children',  # The type of the aggregation
        type='entity',  # The child document type
        aggs={
            'top_files': {
                'terms': {
                    'field': 'entities.parent.keyword',  # The parent document field
                    'size': 10,  # The number of top files to return
                    'order': {'_count': 'desc'},  # Order by count descending
                }
            }
        }
    )

    response = search.execute()

    # Print the results
    for bucket in response.aggregations.files_with_most_entities.top_files.buckets:
        print(f"File ID: {bucket.key}, Entity Count: {bucket.doc_count}")

    file_formats = response.aggregations.file_formats.buckets
    entity_types = response.aggregations.entity_types.buckets
    most_common_values = response.aggregations.most_common_values.buckets

    # Convert AttrList objects to dictionaries
    file_formats = [bucket.to_dict() for bucket in file_formats]
    most_common_values = [bucket.to_dict() for bucket in most_common_values]
    entity_types = [bucket.to_dict() for bucket in entity_types]
    entity_types = list(map(lambda bucket: {**bucket, "key": entity_type_to_czech[bucket["key"]]}, entity_types))

    return render_template("stats.html", file_formats=file_formats, entity_types=entity_types,
                           most_common_values=most_common_values,
                           file_entities=[], form=form)
