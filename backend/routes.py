from flask import render_template, request
from elastic import get_all_datasets, find_entities, get_all_files, get_most_popular_by_type

from backend import app, es
from backend.forms import SearchForm
from backend.models import entities_from_hits

PAGE_SIZE = 10


@app.route("/", methods=["GET", "POST"])
@app.route("/search", methods=["GET", "POST"])
def search():
    form = SearchForm()
    datasets = get_all_datasets(es)
    found_entities = []

    total_hits = 0
    page = request.args.get('page', 1, type=int)
    start_index = (page - 1) * PAGE_SIZE

    if form.validate_on_submit():
        search_term = form.search_term.data
        dataset = form.dataset.data
        entity_type = form.entity_type.data

        total_hits, hits = find_entities(es, search_term, dataset, entity_type, start_index, PAGE_SIZE)

        file_hits = get_all_files(es, dataset)
        found_entities = entities_from_hits(hits, file_hits, search_term)

    return render_template("home.html", form=form, datasets=datasets, found_entites=found_entities,
                           total_hits=total_hits, page=page, page_size=PAGE_SIZE)


@app.route("/stats")
def stats():
    datasets = get_all_datasets(es)
    get_most_popular_by_type(es, "format", "Všechny")
    return render_template("stats.html", datasets=datasets)