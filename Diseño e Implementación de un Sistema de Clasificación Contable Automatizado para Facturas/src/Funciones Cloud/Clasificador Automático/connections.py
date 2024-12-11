from google.cloud import firestore, storage

def getFirestore(databaseId):
    return firestore.Client(database=databaseId)

storage_client = storage.Client()
