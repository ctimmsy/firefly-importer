import requests as r
import urllib3
from models import Transaction

# Suppress only the single InsecureRequestWarning from urllib3
# This will be changed once SSL cert is added.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class FireflyClient:
    def __init__(self, base_url: str, token: str, account_id: int):
        self.base_url = base_url
        self.token = token
        self.req_headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
        }
        self.account_id = account_id

    def import_transaction(self, transaction: Transaction):
        payload = {
            "error_if_duplicate_hash": True,
            "transactions": [
                {
                    "type": transaction.type,
                    "date": transaction.settlement_time,
                    "amount": str(transaction.amount),
                    "description": transaction.description,
                    "external_id": transaction.uid,
                }
            ],
        }

        tx = payload["transactions"][0]

        if transaction.type == "withdrawal":
            tx["source_id"] = str(self.account_id)
            tx["destination_name"] = transaction.counterparty

        elif transaction.type == "deposit":
            tx["destination_id"] = str(self.account_id)
            tx["source_name"] = transaction.counterparty

        res = r.request(
            "POST",
            f"{self.base_url}/transactions",
            headers=self.req_headers,
            json=payload,
            verify=False,
        )
        try:
            res.raise_for_status()
        except r.exceptions.HTTPError:
            print(res.json())
            raise
