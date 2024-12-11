from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from utils import checkKeyWords
from io import BytesIO
import numpy as np
import unicodedata
import joblib
import string
import re
import os


bucket_name = os.environ.get('BUCKET_NAME')

"""
Searches for matching simple classifications based on a description.

Args:
    description (str): The description to search for classifications.
    sender_id (str, optional): The ID of the sender. Defaults to None.
    receiver_id (str, optional): The ID of the receiver. Defaults to None.
    position (str, optional): The position of the classification ('in' or 'out'). Defaults to None.

Returns:
    list: A list of matching classification specifications.
"""
def findMatchingSimpleClassifications(firestore_client, description: str, 
                                    sender_id=None, receiver_id=None, 
                                    position=None) -> list:
    """
    Búsqueda de clasificaciones coincidentes
    """
    try:
        # Asegurarse de que tenemos los recursos NLTK antes de procesar
        if not os.path.exists("/tmp/nltk_data/tokenizers/punkt"):
            download_nltk_data()
        
        classifications_ref = firestore_client.collection('recurrencies')
        query = classifications_ref.where('type', '==', 'invoice_classification')\
                                 .where('active', '==', True)
        
        if position == 'in':
            query = query.where('sender_id', '==', sender_id)
        elif position == 'out':
            query = query.where('receptor_id', '==', receiver_id)
        else:
            raise ValueError("Position must be 'in' or 'out'")
        
        default_classification_recurrency = None
        description = description.lower()
        
        # Procesamiento de texto con manejo de errores
        try:
            # Remover puntuación excepto '-' y '_'
            custom_punctuation = ''.join(c for c in string.punctuation 
                                       if c not in '-_')
            text = description.translate(str.maketrans('', '', custom_punctuation))
            
            # Remover espacios extras
            text = re.sub(r'\s+', ' ', text)
            
            # Tokenización y remoción de stopwords
            stop_words = set(stopwords.words('spanish'))
            word_tokens = word_tokenize(text)
            filtered_text = [word for word in word_tokens 
                           if not word.lower() in stop_words]
            text = ' '.join(filtered_text)
            
            # Normalización de caracteres
            description = unicodedata.normalize('NFKD', text)\
                         .encode('ASCII', 'ignore').decode('utf-8')
            
        except Exception as e:
            print(f"Error en el procesamiento de texto: {str(e)}")
            # En caso de error, usar el texto original
            description = description.lower()
        
        # Búsqueda de coincidencias
        matches = []
        for recurrency in query.stream():
            rec_data = recurrency.to_dict()
            
            if rec_data['specs']['default'] == True:
                default_classification_recurrency = rec_data['specs']
                continue
            
            all_keywords_matched = checkKeyWords(rec_data['specs']['key_words'], 
                                               description)
            
            if all_keywords_matched:
                matches.append(rec_data['specs'])
        
        if not matches and default_classification_recurrency is not None:
            matches.append(default_classification_recurrency)
        
        return matches
        
    except Exception as e:
        print(f"Error en findMatchingSimpleClassifications: {str(e)}")
        # En caso de error, retornar lista vacía o el clasificador por defecto
        return [default_classification_recurrency] if default_classification_recurrency else []



def predictValue(storage_client, value: dict, org_path: str) -> list:
    """
    Predicts the value based on the provided input.

    Args:
        storage_client: The Google Cloud Storage client.
        bucket_name (str): The name of the bucket.
        value (dict): Dictionary containing the input values for prediction.

    Returns:
        list: A list containing the predicted classifications.
    """
    def load_from_gcs(bucket_name, path):
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(path)
        buffer = BytesIO(blob.download_as_bytes())
        return joblib.load(buffer)

    try:
        # Extract 'id', 'position', 'company_tid', and 'total' from the request
        id = value['id']
        position = value['position']
        company = value['company']
        total = value['total']
        
        # Load models and encoders from GCS
        model = load_from_gcs(bucket_name, f'{org_path}/{id}/{position}/models/random_forest_model.joblib')
        label_encoder = load_from_gcs(bucket_name, f'{org_path}/{id}/{position}/models/label_encoder.joblib')
        company_encoder = load_from_gcs(bucket_name, f'{org_path}/{id}/{position}/models/company_encoder.joblib')
        
        try:
            company_array = np.array([company]).reshape(-1, 1)  # Reshape to ensure 2D
            company_encoded = company_encoder.transform(company_array)

            # Convert company_encoded to a dense array if it's a sparse matrix
            if hasattr(company_encoded, "toarray"):
                company_encoded = company_encoded.toarray()

            total_array = np.array([[total]])  # Create a 2D array directly

            # Concatenate for prediction
            sample_for_prediction = np.hstack((company_encoded, total_array))
            
            prediction = model.predict(sample_for_prediction)[0]
            prediction_label = label_encoder.inverse_transform([prediction])[0]

            return [{
                'accounting_classification': prediction_label,
                'analytic_classification': '',
                'default': False
                }]
            
        except Exception as e:
            print(f"Error during preparation or prediction: {e}")
            return [{
                'accounting_classification': '',
                'analytic_classification': '',
                'default': False
                }]
    
    except Exception as e:
        print(f"Error: {e}")
        return [{
                'accounting_classification': '',
                'analytic_classification': '',
                'default': False
                }]


__all__ = [findMatchingSimpleClassifications, predictValue]