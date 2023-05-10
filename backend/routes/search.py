from flask import render_template, request
from flask_paginate import Pagination

from backend import app, es
from backend.forms import SearchForm
from backend.models import entities_from_hits
from elastic import find_entities_with_limit
from functools import reduce


@app.route("/search", methods=["GET", "POST"])
def search():
    form = SearchForm(request.form)

    # initial page load or invalid form data
    if request.method == "GET" or not form.validate_on_submit():
        return render_template("search.html", form=form)

    # form submitted
    page = request.args.get("page", 1, type=int)

    dataset = form.dataset.data
    results_per_page = int(form.results_per_page.data)
    search_terms = form.search_terms.data
    entity_types_list = form.entity_types_list.data
    file_format_list = form.file_format_list.data
    file_language_list = form.file_language_list.data

    hits = find_entities_with_limit(es, dataset, search_terms, entity_types_list, file_format_list, file_language_list,
                                    page, results_per_page)
    total_hits = reduce(lambda total, hit: total + len(hit.entities), hits, 0)

    results = entities_from_hits(hits, file_hits)

    pagination = Pagination(
        page=page,
        total=total_hits,
        per_page=results_per_page,
        css_framework='bootstrap4',
    )

    results_html = render_template('search-results.html', results=results, pagination=pagination,
                                   total_hits=total_hits)

    return {'results': results_html}
