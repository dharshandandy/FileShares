import os
from flask import Flask, request, jsonify, send_from_directory, render_template, redirect, url_for
from werkzeug.utils import secure_filename
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configure the upload folder
TUNNEL_FOLDER = 'tunnel_folder'
os.makedirs(TUNNEL_FOLDER, exist_ok=True)
app.config['TUNNEL_FOLDER'] = TUNNEL_FOLDER

# Helper function to list files
def list_files():
    files = []
    for filename in os.listdir(TUNNEL_FOLDER):
        path = os.path.join(TUNNEL_FOLDER, filename)
        if os.path.isfile(path):
            files.append(filename)
    return files

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/files', methods=['GET'])
def get_files():
    files = list_files()
    return jsonify(files)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['TUNNEL_FOLDER'], filename))
        return jsonify({"success": True}), 200

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory(app.config['TUNNEL_FOLDER'], filename)

@app.route('/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    path = os.path.join(app.config['TUNNEL_FOLDER'], filename)
    if os.path.exists(path):
        os.remove(path)
        return jsonify({"success": True}), 200
    return jsonify({"error": "File not found"}), 404

@app.route('/rename', methods=['POST'])
def rename_file():
    data = request.get_json()
    old_filename = secure_filename(data['old_filename'])
    new_filename = secure_filename(data['new_filename'])
    old_path = os.path.join(app.config['TUNNEL_FOLDER'], old_filename)
    new_path = os.path.join(app.config['TUNNEL_FOLDER'], new_filename)
    if os.path.exists(old_path):
        os.rename(old_path, new_path)
        return jsonify({"success": True}), 200
    return jsonify({"error": "File not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)

