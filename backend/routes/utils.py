import csv
import json
import os
import tempfile
import zipfile

from flask import render_template, request, jsonify
from flask import send_file

from backend import app, es
from backend.forms import SearchForm
from elastic import get_file, find_all_entities, get_filepaths_by_ids
from email_analyzer import run_analysis


def export_csv(dataset, hits):
    with tempfile.NamedTemporaryFile('w', delete=False, encoding='utf-8') as csvfile:
        # Add a UTF-8 BOM at the beginning of the file
        csvfile.write('\ufeff')
        fieldnames = ['dataset', 'file_id', 'entity_type', 'value', 'lemmatized']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for hit in hits:
            dataset = hit.meta.index
            hit = hit.to_dict()
            hit["dataset"] = dataset
            hit["file_id"] = hit["entities"]["parent"]
            writer.writerow({field: value for field, value in hit.items() if field in fieldnames})

    response = send_file(csvfile.name, mimetype='text/csv', as_attachment=True)
    return response


def export_zip(paths):
    with tempfile.NamedTemporaryFile('wb', delete=False, suffix='.zip') as temp_zip:
        with zipfile.ZipFile(temp_zip.name, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
            for file_path in paths:
                zf.write(file_path, os.path.basename(file_path))

    response = send_file(temp_zip.name, mimetype='application/zip', as_attachment=True)
    return response


def get_files_containing_entities(hits):
    ids = set()
    for hit in hits:
        dataset = hit.meta.index
        ids.add((dataset, hit.entities.parent))
    return list(ids)


@app.route("/export", methods=["POST"])
def export():
    allowed_formats = ["csv", "json", "zip"]
    export_format = request.args.get("format", "csv", type=str)
    if export_format not in allowed_formats:
        return jsonify({"error": f"Export format {export_format} not supported"}), 400

    form = SearchForm(request.form)
    if not form.validate_on_submit():
        return jsonify({"error": "Form is not valid"}), 400

    dataset = form.dataset.data
    search_terms = form.search_terms.data
    entity_types_list = form.entity_types_list.data
    file_format_list = form.file_format_list.data
    file_language_list = form.file_language_list.data

    hits = find_all_entities(es, dataset, search_terms, entity_types_list, file_format_list, file_language_list)

    match export_format:
        case "csv":
            return export_csv(dataset, hits)
        case "json":
            return jsonify({"error": "JSON export not implemented yet"}), 400
        case "zip":
            files = get_files_containing_entities(hits)
            paths = get_filepaths_by_ids(es, files)
            return export_zip(paths)


@app.route("/file/<string:dataset>/<string:file_id>")
def show_file(dataset, file_id):
    file = get_file(es, dataset, file_id)
    if not file:
        return jsonify({"error": "File not found"}), 404
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

    entities_search = Search(using=es, index="testovaci_dataset")

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
