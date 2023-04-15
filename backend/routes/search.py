from flask import render_template, request
from flask_paginate import Pagination

from backend import app, es
from backend.forms import SearchForm
from backend.models import entities_from_hits
from elastic import find_entities_with_limit, get_all_files


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