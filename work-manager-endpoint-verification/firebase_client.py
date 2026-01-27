import os
import json
import firebase_admin
from firebase_admin import credentials, db


def init_firebase():
    if firebase_admin._apps:
        return

    firebase_creds_json = open(file="..\..\work-manager-verification-firebase-adminsdk-fbsvc-ccd896a106.json", mode='rb').read()
    
    firebase_db_url = os.getenv(
        "FIREBASE_DB_URL",
        "https://work-manager-verification-default-rtdb.firebaseio.com"
    )

    if not firebase_creds_json:
        raise RuntimeError("FIREBASE_CREDENTIALS not set")

    creds_dict = json.loads(firebase_creds_json)
    cred = credentials.Certificate(creds_dict)

    firebase_admin.initialize_app(cred, {
        "databaseURL": firebase_db_url
    })


def whitelist_ref():
    init_firebase()
    return db.reference("whitelist")
