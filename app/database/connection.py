import structlog
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os

logger = structlog.get_logger(__name__)

# Initialize Firebase Admin SDK
try:
    if not firebase_admin._apps:
        # If GOOGLE_APPLICATION_CREDENTIALS is not set, we can look for a fallback config or just use default
        if 'GOOGLE_APPLICATION_CREDENTIALS' in os.environ:
            cred = credentials.ApplicationDefault()
            firebase_admin.initialize_app(cred)
        else:
            # For local dev without env var, maybe initialize a dummy or assume default credentials
            firebase_admin.initialize_app()
    logger.info("Firebase Admin initialized successfully")
except Exception as e:
    logger.error("Failed to initialize Firebase Admin", error=str(e))

def get_db():
    """Dependency for injecting Firestore client"""
    return firestore.client()
