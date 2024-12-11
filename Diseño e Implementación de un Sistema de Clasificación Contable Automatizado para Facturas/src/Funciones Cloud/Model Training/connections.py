from google.cloud import firestore, storage, secretmanager
import os

def get_secret_from_manager(secret_name):
    project_id = os.getenv("PROJECT_ID")
    secret_version = 'latest'  # Puedes cambiar a una versión específica si es necesario

    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_name}/versions/{secret_version}"

    try:
        response = client.access_secret_version(name=name)
        secret_payload = response.payload.data.decode('UTF-8')
        return secret_payload
    except Exception as e:
        print(f"Failed to access secret: {str(e)}")
        return None


def getFirestore(databaseId):
    return firestore.Client(database=databaseId)
storage_client = storage.Client()
