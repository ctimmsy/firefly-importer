from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime


@dataclass
class Transaction:
    type: str
    uid: str
    amount: Decimal
    description: str
    counterparty: str
    settlement_time: datetime
