import requests as r
from models import Transaction
from decimal import Decimal


class StarlingClient:
    def __init__(self, token: str, account_name: str):
        self.BASE_URL = "https://api.starlingbank.com/api/v2"
        self.token = token
        self.account_name = account_name
        self.req_headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
        }
        self.account_uid, self.account_created_date = self._get_account_details()

    def _get_account_details(self):
        res = r.request(
            "GET",
            f"{self.BASE_URL}/accounts",
            headers=self.req_headers,
        )
        res.raise_for_status()

        accounts_list = res.json()["accounts"]
        for a in accounts_list:
            if a["name"] == self.account_name:
                return a["accountUid"], a["createdAt"]
        raise ValueError(
            f'Failed to find account details for account "{self.account_name}"'
        )

    def get_transactions(self, start_date: str, end_date: str):

        res = r.request(
            "GET",
            f"{self.BASE_URL}/feed/account/{self.account_uid}/settled-transactions-between",
            headers=self.req_headers,
            params={
                "minTransactionTimestamp": start_date,
                "maxTransactionTimestamp": end_date,
            },
        )
        res.raise_for_status()

        trans_raw = res.json()["feedItems"]
        return [
            Transaction(
                "deposit" if t["direction"] == "IN" else "withdrawal",
                t["feedItemUid"],
                Decimal(t["amount"]["minorUnits"]) / Decimal("100"),
                t.get("reference") or "No ref.",
                t.get("counterPartyName") or "Unknown account",
                t["settlementTime"],
            )
            for t in trans_raw
        ]
