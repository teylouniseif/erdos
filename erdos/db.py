import sqlite3


class DB:

    tbl_is_initialized = False

    i = 4

    @staticmethod
    def _init_conversations_tbl():
        if DB.tbl_is_initialized:
            return
        """Initialize the SQLite database and create the table if it doesn't exist."""
        with sqlite3.connect(".conversations.db") as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                    conversation_id INTEGER PRIMARY KEY NOT NULL,
                    conversation TEXT
                )
                """
            )
            conn.commit()
            DB.tbl_is_initialized = True

    @staticmethod
    def store(conversation_id: int, conversation: str):
        """"Store the conversation in the database."""

        with sqlite3.connect(".conversations.db") as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO conversations (conversation_id, conversation)
                VALUES (?, ?)
                """,
                (conversation_id, conversation),
            )
            conn.commit()

    @staticmethod
    def retrieve(conversation_id: int) -> str:
        """Retrieve all messages for the conversation from the database."""
        with sqlite3.connect(".conversations.db") as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT conversation FROM conversations
                WHERE conversation_id = (?)
                ORDER BY conversation_id ASC
                """,
                (conversation_id,),
            )
            rows = cursor.fetchall()

        # Extract messages from query results
        return rows[0][0] if rows else None


DB._init_conversations_tbl()
