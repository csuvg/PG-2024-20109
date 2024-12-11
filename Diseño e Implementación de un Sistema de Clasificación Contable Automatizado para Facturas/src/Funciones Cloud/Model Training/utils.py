from connections import getFirestore, storage_client
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
import os
import json
import pandas as pd
import numpy as np
import joblib


bucket_name = os.environ.get('BUCKET_NAME')

def verifyGCSFolder(company_id, position, path):
    """
    Verifies if a folder exists in a Google Cloud Storage bucket and if it contains at least one .json file.
    Args:
        company_id (str): The company ID.
        position (str): The position identifier.
    Returns:
        tuple: A tuple containing a boolean indicating if the folder exists and is not empty, and a list of JSON file blobs or an error message.
    """
    try:
        bucket = storage_client.bucket(bucket_name)
        prefix = f'{path}/{company_id}/{position}/dataset/'
        blobs = list(bucket.list_blobs(prefix=prefix))
        
        # Check if there is at least one .json file in the folder
        json_files = [blob for blob in blobs if blob.name.endswith('.json')]
        
        if json_files:
            return (True, json_files)
        else:
            return (False, 'The folder exists but contains no .json files')
    except Exception as e:
        return (False, f'Error accessing GCS: {str(e)}')

def prepareData(df, company_tid_encoder):
    """
    Prepares data for model training.
    Args:
        df (pd.DataFrame): The DataFrame containing the data.
        company_tid_encoder (OneHotEncoder): The pre-fitted OneHotEncoder for 'company_tid'.
    Returns:
        np.ndarray: The prepared feature matrix.
    """
    X_sender_id = company_tid_encoder.transform(df[['company']]).toarray()
    unit_total = df['unit_total'].to_numpy().reshape(-1, 1)
    X = np.hstack((X_sender_id, unit_total))
    return X

def encodeTarget(y):
    """
    Encodes target labels.
    Args:
        y: The target labels to encode.
    Returns:
        tuple: A tuple containing the encoded labels and the label encoder.
    """
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    return y_encoded, label_encoder

def trainModel(json_files):
    """
    Trains a RandomForest model by loading JSON files from GCS.
    Args:
        json_files (list): List of blob objects representing JSON files.
    Returns:
        RandomForestClassifier, OneHotEncoder, LabelEncoder: Trained model, feature encoder, and label encoder.
    """
    # Gather all data
    all_data = []
    for blob in json_files:
        json_string = blob.download_as_text()
        json_data = json.loads(json_string)
        all_data.append(pd.DataFrame(json_data))

    # Concatenate all data into a single DataFrame
    df = pd.concat(all_data, ignore_index=True)

    # Drop unnecessary columns and the target column
    print("Column titles: ", df.columns.tolist())
    df = df[df['accounting_classification'].astype(bool)]
    df['accounting_classification'] = df['accounting_classification'].astype(str)

    df['company'] = df['company_tid'] + df['establishment_id']

    # Prepare the data and ensure the target column is not included in X
    company_encoder = OneHotEncoder(handle_unknown='ignore')
    company_encoder.fit(df[['company']])
    X = prepareData(df, company_encoder)
    y, label_encoder = encodeTarget(df['accounting_classification'])

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    # Train the model
    model = RandomForestClassifier(n_estimators=100)
    model.fit(X_train, y_train)

    # Evaluate the model
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f'Random Forest Model Accuracy: {accuracy:.2f}')

    return model, company_encoder, label_encoder

def saveToGCS(company_id, position, model, company_encoder, label_encoder, path):
    """
    Saves the model and encoders to Google Cloud Storage.
    Args:
        company_id (str): The ID of the company.
        position (str): The position related to the model.
        model: The trained model.
        company_tid_encoder: The encoder for the features.
        label_encoder: The encoder for the target labels.
    """
    
    prefix = f'{path}/{company_id}/{position}/'
    
    bucket = storage_client.bucket(bucket_name)
    
    # Save model to a file and upload
    model_filename = '/tmp/random_forest_model.joblib'
    joblib.dump(model, model_filename)
    model_blob = bucket.blob(f'{prefix}models/random_forest_model.joblib')
    model_blob.upload_from_filename(model_filename)
    
    # Save company_encoder to a file and upload
    company_encoder_filename = '/tmp/company_encoder.joblib'
    joblib.dump(company_encoder, company_encoder_filename)
    company_encoder_blob = bucket.blob(f'{prefix}models/company_encoder.joblib')
    company_encoder_blob.upload_from_filename(company_encoder_filename)
    
    # Save label_encoder to a file and upload
    label_encoder_filename = '/tmp/label_encoder.joblib'
    joblib.dump(label_encoder, label_encoder_filename)
    label_encoder_blob = bucket.blob(f'{prefix}models/label_encoder.joblib')
    label_encoder_blob.upload_from_filename(label_encoder_filename)

