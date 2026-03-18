import os
import json
import logging
import firebase_admin
from firebase_admin import credentials

logger = logging.getLogger(__name__)

_app = None


def get_firebase_app():
    global _app
    if _app is not None:
        return _app

    cred_json = os.environ.get('FIREBASE_CREDENTIALS')
    cred_path = os.environ.get('FIREBASE_CREDENTIALS_PATH')

    if not cred_json and not cred_path:
        logger.warning("Firebase credentials not configured. Push notifications will be skipped.")
        return None

    try:
        if cred_json:
            cred = credentials.Certificate(json.loads(cred_json))
        else:
            cred = credentials.Certificate(cred_path)
        _app = firebase_admin.initialize_app(cred)
    except Exception as e:
        logger.error(f"Firebase initialization failed: {e}")
        return None

    return _app
