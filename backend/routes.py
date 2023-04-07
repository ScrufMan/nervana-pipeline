import csv
import json
import os
import tempfile

from flask import render_template, request, jsonify, send_file, after_this_request
from elastic import get_all_datasets, find_entities_with_limit, get_all_files, get_file, get_top_values_for_field, \
    get_top_files_field_values, find_entities

from backend import app, es
from backend.forms import SearchForm
from backend.models import entities_from_hits
from flask_paginate import Pagination
from email_analyzer import run_analysis


@app.route("/search", methods=["GET", "POST"])
# TODO: export to csv, dataset, filename, type, value, context
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

            datset = dataset.split("-entities")[0]
            for hit in hits:
                hit = hit.to_dict()
                hit["dataset"] = dataset
                writer.writerow({field: value for field, value in hit.items() if field in fieldnames})

        response = send_file(csvfile.name, mimetype='text/csv', as_attachment=True, download_name = 'export.csv')
        return response


@app.route("/file/<string:index>/<string:file_id>")
def show_file(index, file_id):
    dataset = index.split("-entities")[0]
    file = get_file(es, dataset, file_id)

    path = file["path"]
    plaintext = file["plaintext"]

    return jsonify({"path": path, "plaintext": plaintext})


@app.route("/")
@app.route("/stats")
def stats():
    datasets = get_all_datasets(es)
    return render_template("stats.html", datasets=datasets)


@app.route("/stats/file-format")
def file_formats():
    data = get_top_files_field_values(es, "_all", "format")
    return json.dumps(data)


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
