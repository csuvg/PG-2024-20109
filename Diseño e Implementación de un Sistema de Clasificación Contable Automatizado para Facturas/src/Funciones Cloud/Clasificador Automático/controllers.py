import numpy as np


def predictValue(value: dict, model_files: dict) -> list:
    """
    Predicts the value based on the provided input.

    Args:
        value (dict): Dictionary containing the input values for prediction.
        model_files (dict): Dictionary containing the loaded model, label encoder, and company encoder.

    Returns:
        list: A list containing the predicted classifications.
    """
    try:
        # Extract 'id', 'position', 'company_tid', and 'total' from the request
        company = value['company']
        total = value['total']

        # Extract the loaded models and encoders
        model = model_files['model']
        label_encoder = model_files['label_encoder']
        company_encoder = model_files['company_encoder']

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

__all__ = [predictValue]
