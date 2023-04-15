from flask import render_template

from backend import app, es
from backend.forms import EntityTypeForm
from elastic import get_all_files


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
    }

    from elasticsearch_dsl import Search

    form = EntityTypeForm()

    files_search = Search(using=es, index="zachyt_1-files")
    entities_search = Search(using=es, index="zachyt_1-entities")

    # Aggregations for graph data
    files_search.aggs.bucket("file_formats", "terms", field="format")
    entities_search.aggs.bucket("entity_types", "terms", field="entity_type")
    entities_search.aggs.bucket("file_entities", "terms", field="file_id", order={"_count": "desc"})
    entities_search.aggs.bucket("most_common_values", "terms", field="lemmatized.keyword")

    files_response = files_search.execute()
    entities_response = entities_search.execute()

    file_formats = files_response.aggregations.file_formats.buckets
    entity_types = entities_response.aggregations.entity_types.buckets
    most_common_values = entities_response.aggregations.most_common_values.buckets

    # Convert AttrList objects to dictionaries
    file_formats = [bucket.to_dict() for bucket in file_formats]
    most_common_values = [bucket.to_dict() for bucket in most_common_values]
    entity_types = [bucket.to_dict() for bucket in entity_types]
    entity_types = list(map(lambda bucket: {**bucket, "key": entity_type_to_czech[bucket["key"]]}, entity_types))

    files = list(get_all_files(es, "zachyt_1"))
    filenames = {file.meta.id: file["filename"] for file in files}
    file_entities = [{**bucket.to_dict(), 'filename': filenames[bucket['key']]} for bucket in
                     entities_response.aggregations.file_entities.buckets]

    return render_template("stats.html", file_formats=file_formats, entity_types=entity_types,
                           most_common_values=most_common_values,
                           file_entities=file_entities, form=form)
