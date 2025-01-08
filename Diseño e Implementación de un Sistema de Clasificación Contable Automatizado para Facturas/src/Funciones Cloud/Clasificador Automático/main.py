from flask import Flask, request, jsonify
from controllers import predictValue
import joblib
import os

# Cargar modelos y encoders en memoria
MODEL_FILES = {
    'model': joblib.load("random_forest_model.joblib"),
    'label_encoder': joblib.load("label_encoder.joblib"),
    'company_encoder': joblib.load("company_encoder.joblib")
}

# Crear instancia de Flask
app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def classification_manager():
    """
    Endpoint para predecir una clasificación basada en los datos de entrada.

    Returns:
        JSON: Clasificación predicha o mensaje de error.
    """
    cors_headers = {"Access-Control-Allow-Origin": "*"}

    if request.method != 'POST':
        return jsonify({"error": "Method not allowed"}), 405, cors_headers

    request_json = request.get_json(silent=True)

    if not request_json:
        return jsonify({"error": "Invalid or missing JSON payload"}), 400, cors_headers

    try:
        # Desempaquetar directamente en variables
        description = request_json.get("description")
        sender_id = request_json.get("sender_id")
        receiver_id = request_json.get("receptor_id")
        establishment_id = request_json.get("establishment_id")
        position = request_json.get("position")
        total = request_json.get("total")

        # Validación de los datos requeridos
        if not all([sender_id, receiver_id, establishment_id, position, total]):
            return jsonify({"error": "Missing required fields"}), 400, cors_headers

        # Preparar entrada para la predicción
        value = {
            'company': (sender_id if position == "out" else receiver_id) + establishment_id,
            'total': total
        }

        # Realizar la predicción
        matches = predictValue(value, MODEL_FILES)

        return jsonify(matches), 200, cors_headers

    except Exception as e:
        print(f"Error during prediction: {e}")
        return jsonify({"error": "An error occurred during prediction."}), 500, cors_headers

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
