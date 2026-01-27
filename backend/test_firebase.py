import os
import firebase_admin
from firebase_admin import credentials, firestore

print("ENV:", os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"))

cred = credentials.Certificate(os.environ["GOOGLE_APPLICATION_CREDENTIALS"])
firebase_admin.initialize_app(cred)

db = firestore.client()
print("Firestore OK:", db)