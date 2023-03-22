from flask import render_template, request
from elastic import get_all_datasets, find_entities, get_all_files, get_most_popular_by_type, get_file

from backend import app, es
from backend.forms import SearchForm
from backend.models import entities_from_hits
from tika import parser
from flask_paginate import Pagination

PAGE_SIZE = 10


@app.route("/search", methods=["GET", "POST"])
def search():
    form = SearchForm(request.form)
    datasets = get_all_datasets(es)

    if request.method == "GET":
        return render_template("search.html", form=form, datasets=datasets)

    page = request.args.get("page", 1, type=int)

    if form.validate():
        dataset = form.dataset.data
        search_terms = form.search_terms.data
        entity_types = form.entity_types.data

        search_conditions = zip(search_terms, entity_types)

        total_hits, hits = find_entities(es, dataset, search_conditions, page, PAGE_SIZE)

        file_hits = get_all_files(es, dataset)
        results = entities_from_hits(hits, file_hits)

        pagination = Pagination(
            page=page,
            total=total_hits,
            per_page=PAGE_SIZE,
            css_framework='bootstrap4',
            link_attr={'class': 'my-link-class'}
        )

        results_html = render_template('search-results.html', results=results, pagination=pagination,
                                       total_hits=total_hits)

        return {'results': results_html}


@app.route("/file/<string:dataset>/<string:file_id>")
def show_file(dataset, file_id):
    file = get_file(es, dataset, file_id)
    path = file["path"]

    tika_response = parser.from_file(path)

    if tika_response["status"] != 200:
        return f"Error extracting plaintext from file {path}"

    plaintext = tika_response["content"]
    plaintext = plaintext.strip()

    return render_template("file.html", path=path, plaintext=plaintext)


@app.route("/stats")
def stats():
    datasets = get_all_datasets(es)
    get_most_popular_by_type(es, "format", "Všechny")
    return render_template("stats.html", datasets=datasets)
