import asyncio
from app.database.connection import get_db

def test_firestore():
    db = get_db()
    print("Got db client, trying to list collections...")
    collections = list(db.collections())
    print("Collections:", collections)

test_firestore()
