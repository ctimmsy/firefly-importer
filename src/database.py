import sqlite3
from datetime import datetime, UTC
from models import Transaction


class DatabaseClient:
    def __init__(
        self,
        db_path: str,
    ):
        self.db_path = db_path

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        with self.get_connection() as conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                uid TEXT PRIMARY KEY,
                settlement_time TEXT,
                imported_at TEXT
            )
            """)

    def import_transaction(self, transaction: Transaction):
        with self.get_connection() as conn:
            conn.execute(
                "INSERT INTO transactions VALUES(?, ?, ?)",
                (
                    transaction.uid,
                    transaction.settlement_time,
                    datetime.now(UTC).isoformat(),
                ),
            )

    def has_been_imported(self, transaction_uid):
        with self.get_connection() as conn:
            res = conn.execute(
                "SELECT 1 FROM transactions WHERE uid = ?",
                (transaction_uid,),
            )

            return res.fetchone() is not None

    def latest_transaction_date(self):
        with self.get_connection() as conn:
            row = conn.execute(
                """
                SELECT MAX(settlement_time)
                FROM transactions
                """
            ).fetchone()

            return row[0]
