from database import DatabaseClient

from firefly import FireflyClient
from starling import StarlingClient
from datetime import datetime, UTC
import os


firefly_token = os.getenv("FFLY_TOKEN")
firefly_url = os.getenv("FFLY_URL")
starling_token = os.getenv("STARLING_TOKEN")
database_path = os.getenv("SQLITE_PATH")


def main():
    if not firefly_token:
        raise ValueError('Environment variable "FFLY_TOKEN" not provided')
    if not firefly_url:
        raise ValueError('Environment variable "FFLY_URL" not provided')
    if not starling_token:
        raise ValueError('Environment variable "STARLING_TOKEN" not provided')
    if not database_path:
        raise ValueError('Environment variable "SQLITE_PATH" not provided')

    db = DatabaseClient(database_path)
    db.init_db()
    ffly = FireflyClient(firefly_url, firefly_token)
    starling = StarlingClient(starling_token, "Starling")

    since = db.latest_transaction_date()
    if since is None:
        print("first run")
        since = starling.account_created_date
    else:
        print(f"fetching transactions since {since}")

    transactions = starling.get_transactions(since, datetime.now(UTC).isoformat())

    for transaction in transactions:
        if db.has_been_imported(transaction.uid):
            print(f"Transaction: {transaction.uid} already imported")
            continue
        ffly.import_transaction(transaction, 725)
        db.import_transaction(transaction)


if __name__ == "__main__":
    main()
