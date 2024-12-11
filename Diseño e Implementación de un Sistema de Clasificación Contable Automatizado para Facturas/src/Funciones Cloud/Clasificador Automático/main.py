#####################################################################################################################
__author__ = "Juan Carlos Bajan"
__copyright__ = "ARO Copyright 2023-2024"
__credits__ = "Olive Tech Guatemala"
__maintainer__ = "Olive Tech Guatemala"
__license__ = "GPL"
__version__ = "2.0.0"
__status__ = "Production"

# ! ===> Classification Manager <===

"""
Verifies the validity of the request method and client's IP address.
Parses JSON data from the request and validates its structure.
Retrieves company information based on sender or receiver ID.
Performs classification based on the company's plan (simple or advanced).
"""
#####################################################################################################################

from controllers import findMatchingSimpleClassifications, predictValue
from connections import storage_client, getFirestore
from schemas import notificationSchema
from voluptuous import MultipleInvalid
from flask import jsonify
import nltk 
import os 
from google.cloud import storage
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Configurar el directorio de datos NLTK en /tmp (directorio escribible en Cloud Functions)
nltk.data.path.append("/tmp/nltk_data")

def download_nltk_data():
    """Descarga los recursos NLTK necesarios al directorio temporal"""
    if not os.path.exists("/tmp/nltk_data"):
        os.makedirs("/tmp/nltk_data")
    
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', download_dir="/tmp/nltk_data")
    
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords', download_dir="/tmp/nltk_data")

"""
Main function called when the Google Cloud Function (GCF) starts.
    
Args:
    request: The HTTP request object.

Returns:
    dict: The classification matches as a JSON response.
"""
def classification_manager(request) -> dict:

    # Verify Request
    cors_headers = {"Access-Control-Allow-Origin": "*"}
    if not request.method == 'POST':
        return jsonify({"error": "Method not allowed"}), 405, cors_headers

    # Get Notification
    request_json = request.get_json(silent=True)
    
    # Validate Notification Structure
    try:
        notificationSchema(request_json)
    except MultipleInvalid as e:
            errors = []
            for error in e.errors:
                error_path = ".".join(str(p) for p in error.path)
                errors.append(f"{error_path}: {error.msg}")
            return jsonify({"error": ", ".join(errors)}), 400, cors_headers
    except Exception as e:
        return jsonify({"error": e}), 400, cors_headers
    
    download_nltk_data()

    # Desempaquetar directamente en variables
    description, sender_id, receiver_id, establishment_id, position, total, path = (
        request_json.get("description"),
        request_json.get("sender_id"),
        request_json.get("receptor_id"),
        request_json.get("establishment_id"),
        request_json.get("position"),
        request_json.get("total"),
    )

    firestore_client = getFirestore("(default)")

    #Get Company
    company_tid = sender_id if position == "in" else receiver_id
    compania_query = firestore_client.collection('companies').where('tid', '==', company_tid).where('is_associated_company', '==', True)
    results = compania_query.get()
    if not results:
        return jsonify({"error": "Not Associated Company"}), 400, cors_headers
    company = results[0].to_dict()

    # Classificate depending on the company plan

    # Recurrencies
    if company['plan'] == 'simple':
        matches = findMatchingSimpleClassifications(firestore_client, description, sender_id, receiver_id, position)

    # ML Model
    elif company['plan'] == 'advanced':
        matches = predictValue(storage_client ,{
            'id': company['id'],
            'position':position,
            'company': (sender_id if position == "out" else receiver_id) + establishment_id,
            'total': total
        }, path)

    # Not Managed Plan
    else:
        return jsonify({"error": "Not Managed Plan"}), 400, cors_headers

    return jsonify(matches), 200, cors_headers