#####################################################################################################################
__author__ = "Juan Carlos Bajan"
__copyright__ = "ARO Copyright 2023-2024"
__credits__ = "Olive Tech Guatemala"
__maintainer__ = "Olive Tech Guatemala"
__license__ = "GPL"
__version__ = "2.0.0"
__status__ = "Production"

# ! ===> ML Model Generator <===

#####################################################################################################################

from utils import verifyGCSFolder, trainModel, saveToGCS
from schemas import notificationSchema
from voluptuous import MultipleInvalid
import functions_framework
from flask import jsonify
import json

# Configuration constants
ACCEPTED_PLANS = ['advanced', 'ai']

@functions_framework.http
def ml_model_generator(request):
    """
    Trains a machine learning model and saves it to Google Cloud Storage.

    Args:
        request: The HTTP request.

    Returns:
        Tuple: A tuple containing a response message, status code, and headers.
    """
    # Verify CORS
    headers = verifyCors(request)
    if request.method == 'OPTIONS':
        return ('', 204, headers)

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
            return (jsonify({"error": ", ".join(errors)}), 400, headers)
    except Exception as e:
        return (jsonify({"error": e}), 400, headers)

    # Desempaquetar directamente en variables
    token, company_id, position = (
        request_json.get("token"),
        request_json.get("company_id"),
        request_json.get("position")
    )

    # verify GCS Folder
    exists, result = verifyGCSFolder(company_id, position, "(default)")

    if exists:
        json_files = result
        model, company_encoder, label_encoder = trainModel(json_files)
        saveToGCS(company_id, position, model, company_encoder, label_encoder, "(default)")
        return ('Model trained and encoders saved successfully', 200, headers)
    else:
        return (f'Folder verification failed: {result}', 404, headers)
