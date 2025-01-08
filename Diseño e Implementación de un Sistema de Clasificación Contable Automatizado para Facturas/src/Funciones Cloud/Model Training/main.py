import os
import json
import pandas as pd
import numpy as np
import joblib
from flask import Flask, request, jsonify
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from voluptuous import MultipleInvalid
from schemas import notificationSchema

app = Flask(__name__)

# Configuration constants
JSON_FOLDER = 'jsons'  # Carpeta donde están los archivos JSON

def loadJsonFiles():
    """
    Carga todos los archivos JSON de una carpeta específica.
    Returns:
        list: Lista de rutas a los archivos JSON.
    """
    try:
        json_files = [os.path.join(JSON_FOLDER, f) for f in os.listdir(JSON_FOLDER) if f.endswith('.json')]
        if not json_files:
            raise FileNotFoundError('No se encontraron archivos JSON en la carpeta especificada.')
        return json_files
    except Exception as e:
        raise RuntimeError(f'Error cargando archivos JSON: {str(e)}')

def prepareData(df, company_tid_encoder):
    X_sender_id = company_tid_encoder.transform(df[['company']]).toarray()
    unit_total = df['unit_total'].to_numpy().reshape(-1, 1)
    X = np.hstack((X_sender_id, unit_total))
    return X

def encodeTarget(y):
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    return y_encoded, label_encoder

def trainModel(json_files):
    all_data = []
    for json_file in json_files:
        with open(json_file, 'r') as f:
            json_data = json.load(f)
            all_data.append(pd.DataFrame(json_data))

    df = pd.concat(all_data, ignore_index=True)

    df = df[df['accounting_classification'].astype(bool)]
    df['accounting_classification'] = df['accounting_classification'].astype(str)
    df['company'] = df['company_tid'] + df['establishment_id']

    company_encoder = OneHotEncoder(handle_unknown='ignore')
    company_encoder.fit(df[['company']])
    X = prepareData(df, company_encoder)
    y, label_encoder = encodeTarget(df['accounting_classification'])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    model = RandomForestClassifier(n_estimators=100)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f'Precisión del modelo Random Forest: {accuracy:.2f}')

    return model, company_encoder, label_encoder

def saveToLocal(model, company_encoder, label_encoder):
    os.makedirs(JSON_FOLDER, exist_ok=True)

    model_path = os.path.join(JSON_FOLDER, 'random_forest_model.joblib')
    joblib.dump(model, model_path)

    encoder_path = os.path.join(JSON_FOLDER, 'company_encoder.joblib')
    joblib.dump(company_encoder, encoder_path)

    label_path = os.path.join(JSON_FOLDER, 'label_encoder.joblib')
    joblib.dump(label_encoder, label_path)

@app.route('/ml_model_generator', methods=['POST'])
def ml_model_generator():
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    }
    if request.method == 'OPTIONS':
        return ('', 204, headers)

    request_json = request.get_json(silent=True)

    try:
        notificationSchema(request_json)
    except MultipleInvalid as e:
        errors = [f"{'.'.join(str(p) for p in error.path)}: {error.msg}" for error in e.errors]
        return (jsonify({"error": ", ".join(errors)}), 400, headers)
    except Exception as e:
        return (jsonify({"error": str(e)}), 400, headers)

    try:
        json_files = loadJsonFiles()
        model, company_encoder, label_encoder = trainModel(json_files)
        saveToLocal(model, company_encoder, label_encoder)
        return ('Modelo entrenado y encoders guardados localmente con éxito', 200, headers)
    except Exception as e:
        return (jsonify({"error": str(e)}), 500, headers)

if __name__ == '__main__':
    app.run(debug=True)
