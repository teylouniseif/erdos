from erdos.db import DB
import sqlite3


def test_store():
    """Test if the store method inserts and updates correctly."""
    DB._init_conversations_tbl()

    # Store a conversation
    DB.store(1, "Hello, World!")

    # Verify the record
    with sqlite3.connect(".conversations.db") as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT conversation FROM conversations WHERE conversation_id = ?", (1,))
        row = cursor.fetchone()

    DB.store(1, "Goodbye, World!")

    # Verify the updated record
    with sqlite3.connect(".conversations.db") as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT conversation FROM conversations WHERE conversation_id = ?", (1,))
        row = cursor.fetchone()

    assert row is not None
    assert row[0] == "Goodbye, World!"


def test_retrieve_existing_record():
    """Test if the retrieve method retrieves an existing record."""
    DB._init_conversations_tbl()

    # Store a conversation
    DB.store(1, "Hello, World!")

    # Retrieve the conversation
    conversation = DB.retrieve(1)

    assert conversation == "Hello, World!"
