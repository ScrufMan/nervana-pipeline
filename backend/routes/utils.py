import csv
import json
import os
import tempfile

from flask import render_template, request, jsonify
from flask import send_file

from backend import app, es
from backend.forms import SearchForm
from elastic import get_file, find_all_entities
from email_analyzer import run_analysis


@app.route("/export-csv", methods=["POST"])
def export_csv():
    form = SearchForm(request.form)

    if form.validate_on_submit():
        dataset = form.dataset.data
        search_terms = form.search_terms.data
        entity_types_list = form.entity_types_list.data

        hits = find_all_entities(es, dataset, search_terms, entity_types_list)

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
