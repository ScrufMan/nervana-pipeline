import json

from flask import render_template, request, jsonify
from elastic import get_all_datasets, find_entities, get_all_files, get_file, get_top_values_for_field, \
    get_top_files_field_values

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

    hits = find_entities(es, dataset, search_terms, entity_types_list, page, results_per_page)
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
