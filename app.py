from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import json
import re
import time

import comparateur
import pdf_json
import delete_contract
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create Flask app instance
app = Flask(__name__)

# Configurations
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['EXTRACTIONS_FOLDER'] = 'extractions'
app.config['GOOGLE_API_KEY'] = os.getenv('GOOGLE_API_KEY')  # Explicit usage of environment variable

# Debug log to verify API key is loaded (DO NOT log sensitive info in production)
print(f"DEBUG: GOOGLE_API_KEY loaded as: {app.config['GOOGLE_API_KEY']}")

# Ensure folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['EXTRACTIONS_FOLDER'], exist_ok=True)

# Enable CORS
CORS(app)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/extractor')
def extractor():
    return render_template('extractor.html')

@app.route('/extract', methods=['POST'])
def extract_data():
    print("--- Extract data route hit ---")

    if 'pdf_file' not in request.files:
        print("ERROR: 'pdf_file' not in request.files")
        return jsonify({"error": "No PDF file provided"}), 400
    
    pdf_file = request.files['pdf_file']
    level_name = request.form.get('level_name')

    print(f"Received file: {pdf_file.filename}")
    print(f"Received level name: {level_name}")

    if pdf_file.filename == '':
        print("ERROR: No selected file")
        return jsonify({"error": "No selected file"}), 400

    if not level_name:
        print("ERROR: No level name provided")
        return jsonify({"error": "No level name provided"}), 400

    filename = secure_filename(pdf_file.filename)
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    print(f"Saving file to: {pdf_path}")
    pdf_file.save(pdf_path)

    response_payload = None
    status_code = 500

    try:
        print("Calling extract_contract_level_from_pdf...")
        extracted_data = pdf_json.extract_contract_level_from_pdf(pdf_path, level_name)
        print(f"Data returned from extraction: {extracted_data}")

        if isinstance(extracted_data, str):
            match = re.search(r'```json\s*([\s\S]*?)\s*```', extracted_data)
            json_string = match.group(1) if match else extracted_data
            parsed_json = json.loads(json_string)

            timestamp = int(time.time())
            original_filename = os.path.splitext(filename)[0]
            output_filename = f"{timestamp}_{original_filename}.json"
            output_path = os.path.join(app.config['EXTRACTIONS_FOLDER'], output_filename)

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(parsed_json, f, ensure_ascii=False, indent=4)

            print(f"Successfully stored extraction in {output_path}")
            response_payload = parsed_json
            status_code = 200

        elif isinstance(extracted_data, dict) and 'error' in extracted_data:
            print(f"ERROR from extraction function: {extracted_data['error']}")
            response_payload = extracted_data
            status_code = 400

        else:
            print(f"ERROR: Unexpected data format from extraction function: {type(extracted_data)}")
            response_payload = {"error": "Unexpected data format received from extraction function."}
            status_code = 500

    except json.JSONDecodeError:
        print(f"ERROR: Failed to parse JSON from model output. Raw output: {extracted_data}")
        response_payload = {"error": "Failed to parse extraction result", "details": extracted_data}
        status_code = 500
    except Exception as e:
        print(f"An unexpected error occurred in /extract: {e}")
        response_payload = {"error": "An unexpected server error occurred."}
        status_code = 500
    finally:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
            print(f"Cleaned up local upload: {pdf_path}")

    return jsonify(response_payload), status_code

@app.route('/compare', methods=['POST'])
def compare_contracts():
    user_data = request.json
    top_contracts_md = comparateur.find_top_contracts(user_data)

    if isinstance(top_contracts_md, dict) and 'error' in top_contracts_md:
        return jsonify(top_contracts_md), 500

    return jsonify({"table": top_contracts_md})

@app.route('/api/contracts', methods=['GET'])
def get_contracts():
    """Retourne le fichier contracts.json pour le frontend"""
    try:
        contracts_path = os.path.join(os.path.dirname(__file__), 'contracts.json')
        with open(contracts_path, 'r', encoding='utf-8') as f:
            contracts = json.load(f)
        print(f"✅ Contracts.json servi avec succès: {len(contracts)} contrats")
        return jsonify(contracts), 200
    except FileNotFoundError:
        print("❌ Erreur: contracts.json non trouvé")
        return jsonify({"error": "contracts.json not found"}), 404
    except Exception as e:
        print(f"❌ Erreur lors du chargement de contracts.json: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/contracts/delete/<level_id>', methods=['DELETE'])
def delete_contract_endpoint(level_id):
    success, message = delete_contract.delete_contract_by_id(level_id)
    if success:
        return jsonify({"success": True, "message": message}), 200
    else:
        return jsonify({"success": False, "message": message}), 404

if __name__ == '__main__':
    # Important: Flask only loads .env on fresh start
    app.run(debug=True)
