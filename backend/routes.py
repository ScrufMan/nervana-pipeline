import csv
import json
import os
import tempfile

from flask import render_template, request, jsonify, send_file
from elastic import get_all_datasets, find_entities_with_limit, get_all_files, get_file, get_top_values_for_field, \
    get_top_files_field_values, find_entities

from backend import app, es
from backend.forms import SearchForm, EntityTypeForm
from backend.models import entities_from_hits
from flask_paginate import Pagination
from email_analyzer import run_analysis


@app.route("/search", methods=["GET", "POST"])
def search():
    form = SearchForm(request.form)

    if request.method == "GET" or not form.validate_on_submit():
        return render_template("search.html", form=form)

    # Handle api call for ajax
    page = request.args.get("page", 1, type=int)

    dataset = form.dataset.data
    search_terms = form.search_terms.data
    entity_types_list = form.entity_types_list.data
    results_per_page = int(form.results_per_page.data)

    hits = find_entities_with_limit(es, dataset, search_terms, entity_types_list, page, results_per_page)
    total_hits = hits.hits.total.value

    file_hits = get_all_files(es, dataset)
    results = entities_from_hits(hits, file_hits)

    pagination = Pagination(
        page=page,
        total=total_hits,
        per_page=results_per_page,
        css_framework='bootstrap4',
        link_attr={'class': 'my-link-class'}
    )

    results_html = render_template('search-results.html', results=results, pagination=pagination,
                                   total_hits=total_hits, form=form)

    return {'results': results_html}


@app.route("/export-csv", methods=["POST"])
def export_csv():
    form = SearchForm(request.form)

    if form.validate_on_submit():
        dataset = form.dataset.data
        search_terms = form.search_terms.data
        entity_types_list = form.entity_types_list.data

        hits = find_entities(es, dataset, search_terms, entity_types_list)

        # Create a temporary file to store the CSV data
        with tempfile.NamedTemporaryFile('w', delete=False, encoding='utf-8') as csvfile:
            # Add a UTF-8 BOM at the beginning of the file
            csvfile.write('\ufeff')
            fieldnames = ['dataset', 'file_id', 'entity_type', 'value', 'lemmatized']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for hit in hits:
                hit = hit.to_dict()
                hit["dataset"] = dataset if dataset != "all" else "Všechny"
                writer.writerow({field: value for field, value in hit.items() if field in fieldnames})

        response = send_file(csvfile.name, mimetype='text/csv', as_attachment=True)
        return response


@app.route("/file/<string:index>/<string:file_id>")
def show_file(index, file_id):
    dataset = index.split("-entities")[0]
    file = get_file(es, dataset, file_id)

    path = file["path"]
    plaintext = file["plaintext"]

    return jsonify({"path": path, "plaintext": plaintext})


@app.route('/download-file/<path:file_path>')
def download_file(file_path):
    absolute_file_path = os.path.abspath(file_path)

    if not os.path.exists(absolute_file_path):
        return jsonify({'error': 'File not found'}), 404

    return send_file(absolute_file_path, as_attachment=True)


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


@app.route("/update-graph", methods=["GET"])
def update_graph():
    from elasticsearch_dsl import Search

    most_common_entity_type = request.args.get("entity_type", "all")

    entities_search = Search(using=es, index="zachyt_1-entities")

    if most_common_entity_type != "all":
        entities_search = entities_search.filter('term', entity_type=most_common_entity_type)

    entities_search.aggs.bucket("most_common_values", "terms", field="lemmatized.keyword")

    entities_response = entities_search.execute()
    most_common_values = entities_response.aggregations.most_common_values.buckets
    most_common_values = [bucket.to_dict() for bucket in most_common_values]

    return jsonify(most_common_values)

@app.route("/email")
def email():
    return render_template("email.html")


@app.route("/email-graph")
def email_graph():
    graph, pos = run_analysis(r"C:\Users\bukaj\code\school\bakalarka\email_analyzer\sample_emails")

    # Convert the graph data into a JSON format that D3.js can understand
    nodes = [{"id": str(n), "x": pos[n][0], "y": pos[n][1]} for n in graph.nodes()]
    links = [{"source": str(u), "target": str(v)} for u, v in graph.edges()]

    data = {"nodes": nodes, "links": links}
    json_data = json.dumps(data)

    return render_template("email.html", data=json_data)
