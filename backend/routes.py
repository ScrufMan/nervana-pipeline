from flask import render_template
from elastic import get_all_datasets, find_entities, get_all_files

from backend import app, es
from backend.forms import SearchForm
from backend.models import entities_from_hits


@app.route("/", methods=["GET", "POST"])
@app.route("/home", methods=["GET", "POST"])
def home():
    form = SearchForm()
    datasets = get_all_datasets(es)
    found_entities = []

    if form.validate_on_submit():
        search_term = form.search_term.data
        dataset = form.dataset.data
        entity_type = form.entity_type.data
        hits = find_entities(es, search_term, dataset, entity_type)
        file_hits = get_all_files(es, dataset)
        found_entities = entities_from_hits(hits, file_hits, search_term)

    return render_template("home.html", form=form, datasets=datasets, found_entites=found_entities)
